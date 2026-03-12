import uuid
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from graph.workflow import resort_graph
from memory.conversation_store import redis_client
from memory.conversation_store import get_context, update_context, clear_context

from routes.menu import menu_bp

app = Flask(__name__)
app.register_blueprint(menu_bp)

# ---------------- Health Check ----------------
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Resort Agentic AI (LangGraph Hybrid) is running"
    })

# ---------------- Redis Health Check -----------
@app.route("/health/redis", methods=["GET"])
def redis_health_check():
    try:
        pong = redis_client.ping()
        return jsonify({
            "status": "ok",
            "redis": "connected" if pong else "not responding"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "redis": "disconnected",
            "details": str(e)
        }), 500

# ---------------- Chat Endpoint ----------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    message = data["message"].strip()
    conversation_id = data.get("conversation_id")

    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    # 🔑 Load existing in-memory context (temporary until Redis migration)
    context = get_context(conversation_id)

    # ---------------- Build LangGraph state ----------------
    state = {
        "conversation_id": conversation_id,
        "user_message": message,

        # Backward compatibility:
        # old system used "intent"
        # new graph uses "active_intent"
        "active_intent": context.get("active_intent") or context.get("intent"),

        # Workflow stage
        "stage": context.get("stage"),

        # Restaurant fields
        "item": context.get("item"),
        "price": context.get("price"),
        "quantity": context.get("quantity"),
        "room_number": context.get("room_number"),

        # Room service fields
        "request_type": context.get("request_type"),

        # Optional history (can expand later)
        "history": [],

        # Completion flag (fresh per request)
        "completed": False
    }

    # ---------------- LangGraph Orchestration ----------------
    result = resort_graph.invoke(state)

    # ---------------- Persist or Clear Context ----------------
    if result.get("completed"):
        clear_context(conversation_id)
    else:
        update_context(conversation_id, {
            # Keep BOTH keys during migration
            "active_intent": result.get("active_intent"),
            "intent": result.get("active_intent"),   # backward compatibility

            "stage": result.get("stage"),

            # Restaurant fields
            "item": result.get("item"),
            "price": result.get("price"),
            "quantity": result.get("quantity"),
            "room_number": result.get("room_number"),

            # Room service fields
            "request_type": result.get("request_type"),
        })

    # ---------------- Response ----------------
    return jsonify({
        "conversation_id": conversation_id,
        "intent": result.get("active_intent"),
        "reply": result.get("response", "Sorry, something went wrong.")
    })


# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)