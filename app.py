import uuid
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from agents.router_agent import route_query
from agents.receptionist_agent import handle_reception_query
from agents.restaurant_agent import handle_restaurant_query
from agents.room_service_agent import handle_room_service_query
from memory.conversation_store import get_context, update_context

from routes.menu import menu_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.register_blueprint(menu_bp)

# ---------------- Health Check ----------------
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Resort Agentic AI is running"
    })

# ---------------- Chat Endpoint ----------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    message = data["message"]
    conversation_id = data.get("conversation_id")

    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    # 🔑 Fetch conversation context
    context = get_context(conversation_id)

    # 🔒 INTENT LOCKING LOGIC
    if context.get("stage") and context.get("intent"):
        intent = context["intent"]
    else:
        intent = route_query(message, conversation_id)
        update_context(conversation_id, {"intent": intent})

    # ---------------- Agent Routing ----------------
    if intent == "RECEPTION":
        reply = handle_reception_query(message, conversation_id)

    elif intent == "RESTAURANT":
        reply = handle_restaurant_query(message, conversation_id)

    elif intent == "ROOM_SERVICE":
        reply = handle_room_service_query(message, conversation_id)

    else:
        reply = "Sorry, I couldn't understand your request."

    return jsonify({
        "conversation_id": conversation_id,
        "intent": intent,
        "reply": reply
    })

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
