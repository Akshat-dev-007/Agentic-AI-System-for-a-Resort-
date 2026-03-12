# agents_LG/room_service_nodes.py

from datetime import datetime
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from db import SessionLocal
from models.service_request import ServiceRequest
from graph.state import ResortState

load_dotenv()


# ---------------- LLM (fallback only) ----------------
def get_room_service_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2
    )


ROOM_SERVICE_PROMPT = ChatPromptTemplate.from_template("""
You are a Room Service Agent for a resort.

You can handle:
- Room cleaning
- Laundry service
- Extra amenities

Rules:
- Do NOT hallucinate
- Ask for missing info politely
- Be concise

User message:
{message}
""")


# ---------------- Helpers ----------------
def _extract_room_number(message: str) -> str | None:
    match = re.search(r"\b\d{3}\b", message)
    return match.group(0) if match else None


def _identify_request_type(message: str) -> str:
    message = message.lower()

    if "clean" in message:
        return "Room Cleaning"
    if "laundry" in message:
        return "Laundry Service"
    if any(word in message for word in ["toiletries", "toothpaste", "pillow", "blanket"]):
        return "Extra Amenities"

    return "General Room Service"


def _is_completion_message(message: str) -> bool:
    message = message.lower()
    return any(
        phrase in message
        for phrase in [
            "done",
            "completed",
            "finished",
            "thanks for cleaning",
            "cleaning done",
            "service completed"
        ]
    )


# ---------------- Main LangGraph Node ----------------
def room_service_node(state: ResortState) -> ResortState:
    """
    LangGraph room service workflow node.
    Deterministic for request logging and completion updates.
    LLM fallback only for general support text.
    """
    db = SessionLocal()

    try:
        message = state["user_message"]
        stage = state.get("stage")

        # ---------------- 1️⃣ Completion detection ----------------
        if _is_completion_message(message):
            room_number = _extract_room_number(message)

            if not room_number:
                return {
                    **state,
                    "response": "Please mention your room number so I can update the service status."
                }

            service_request = (
                db.query(ServiceRequest)
                .filter_by(room_number=room_number, status="Pending")
                .order_by(ServiceRequest.created_at.desc())
                .first()
            )

            if not service_request:
                return {
                    **state,
                    "response": "I couldn't find any pending service request for that room."
                }

            service_request.status = "Completed"
            db.commit()

            return {
                "conversation_id": state["conversation_id"],
                "user_message": state["user_message"],
                "response": (
                    f"✅ Your room service request for room {room_number} has been marked as COMPLETED.\n"
                    "Thank you for confirming!"
                ),
                "active_intent": None,
                "stage": None,
                "history": [],
                "completed": True
            }

        # ---------------- 2️⃣ New request ----------------
        if stage is None:
            request_type = _identify_request_type(message)

            return {
                **state,
                "request_type": request_type,
                "stage": "awaiting_room",
                "response": "Sure. Please provide your room number so I can log the request."
            }

        # ---------------- 3️⃣ Capture room number ----------------
        if stage == "awaiting_room":
            room_number = _extract_room_number(message)

            if not room_number:
                return {
                    **state,
                    "response": "Please provide a valid room number."
                }

            service_request = ServiceRequest(
                room_number=room_number,
                request_type=state["request_type"],
                status="Pending",
                created_at=datetime.utcnow()
            )

            db.add(service_request)
            db.commit()

            return {
                "conversation_id": state["conversation_id"],
                "user_message": state["user_message"],
                "response": (
                    "✅ Your request has been logged successfully.\n"
                    f"Request type: {state['request_type']}\n"
                    f"Room number: {room_number}\n"
                    "Status: Pending"
                ),
                "active_intent": None,
                "stage": None,
                "history": [],
                "completed": True
            }

        # ---------------- 4️⃣ Fallback ----------------
        llm = get_room_service_llm()
        chain = ROOM_SERVICE_PROMPT | llm
        response = chain.invoke({"message": message}).content

        return {
            **state,
            "response": response
        }

    finally:
        db.close()