from datetime import datetime
import re

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from db import SessionLocal
from models.service_request import ServiceRequest
from memory.conversation_store import (
    get_context,
    update_context,
    clear_context
)

# ---------------- LLM (fallback only) ----------------
llm = ChatOpenAI(
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

# ---------------- Handler ----------------
def handle_room_service_query(message: str, conversation_id: str) -> str:
    db = SessionLocal()
    context = get_context(conversation_id)
    message_lower = message.lower()

    # ---------------- 1️⃣ Completion detection ----------------
    if _is_completion_message(message):
        room_number = _extract_room_number(message)

        if not room_number:
            db.close()
            return "Please mention your room number so I can update the service status."

        service_request = (
            db.query(ServiceRequest)
            .filter_by(room_number=room_number, status="Pending")
            .order_by(ServiceRequest.created_at.desc())
            .first()
        )

        if not service_request:
            db.close()
            return "I couldn't find any pending service request for that room."

        service_request.status = "Completed"
        db.commit()
        db.close()

        clear_context(conversation_id)

        return (
            f"✅ Your room service request for room {room_number} has been marked as COMPLETED.\n"
            "Thank you for confirming!"
        )

    # ---------------- 2️⃣ New request ----------------
    if "request_type" not in context:
        request_type = _identify_request_type(message)

        update_context(conversation_id, {
            "request_type": request_type,
            "stage": "awaiting_room"
        })

        db.close()
        return "Sure. Please provide your room number so I can log the request."

    # ---------------- 3️⃣ Capture room number ----------------
    if context.get("stage") == "awaiting_room":
        room_number = _extract_room_number(message)

        if not room_number:
            db.close()
            return "Please provide a valid room number."

        service_request = ServiceRequest(
            room_number=room_number,
            request_type=context["request_type"],
            status="Pending",
            created_at=datetime.utcnow()
        )

        db.add(service_request)
        db.commit()
        db.close()

        clear_context(conversation_id)

        return (
            "✅ Your request has been logged successfully.\n"
            f"Request type: {context['request_type']}\n"
            f"Room number: {room_number}\n"
            "Status: Pending"
        )

    # ---------------- 4️⃣ Fallback ----------------
    chain = ROOM_SERVICE_PROMPT | llm
    response = chain.invoke({"message": message}).content
    db.close()
    return response
