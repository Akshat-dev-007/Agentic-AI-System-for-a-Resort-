import re
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from db import SessionLocal
from models.room import Room
from memory.conversation_store import (
    get_context,
    update_context,
    clear_context
)

# ---------------- LLM (FAQ fallback only) ----------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2
)

# ---------------- Prompt ----------------
RECEPTIONIST_PROMPT = ChatPromptTemplate.from_template("""
You are a Receptionist Agent for a resort.

Known Information:
- Check-in time: 10:00 AM
- Check-out time: 11:00 AM
- Facilities:
  • Gym (6 AM – 10 PM)
  • Swimming Pool (7 AM – 9 PM)
  • Spa (10 AM – 8 PM)

Rules:
- Use ONLY the information provided above
- Do NOT hallucinate room availability
- Be polite, concise, and professional

User message:
{message}
""")

# ---------------- Helpers ----------------
def _extract_room_number(message: str) -> str | None:
    match = re.search(r"\b\d{3}\b", message)
    return match.group(0) if match else None


# ---------------- Handler ----------------
def handle_reception_query(message: str, conversation_id: str) -> str:
    db = SessionLocal()
    context = get_context(conversation_id)
    stage = context.get("stage")
    message_lower = message.lower()

    # ---------------- 1️⃣ Room booking intent ----------------
    if stage is None and ("book" in message_lower and "room" in message_lower):
        available_rooms = db.query(Room).filter_by(is_available=True).all()
        room_numbers = [r.room_number for r in available_rooms]

        if not room_numbers:
            db.close()
            return "Sorry, no rooms are currently available."

        update_context(conversation_id, {
            "stage": "awaiting_room_selection"
        })

        db.close()
        return (
            f"The following rooms are available: {room_numbers}\n"
            "Please tell me which room you'd like to book."
        )

    # ---------------- 2️⃣ Room selection ----------------
    if stage == "awaiting_room_selection":
        room_number = _extract_room_number(message)

        if not room_number:
            db.close()
            return "Please provide a valid room number from the available options."

        room = db.query(Room).filter_by(
            room_number=room_number,
            is_available=True
        ).first()

        if not room:
            db.close()
            return "That room is not available. Please choose another room."

        room.is_available = False
        db.commit()

        clear_context(conversation_id)
        db.close()

        return f"✅ Room {room_number} has been successfully booked for you!"

    # ---------------- 3️⃣ Checkout intent ----------------
    if "check out" in message_lower or "checkout" in message_lower:
        room_number = _extract_room_number(message)

        if not room_number:
            db.close()
            return "Please tell me your room number to proceed with check-out."

        room = db.query(Room).filter_by(room_number=room_number).first()

        if not room:
            db.close()
            return "I couldn't find that room number. Please check and try again."

        room.is_available = True
        db.commit()

        clear_context(conversation_id)
        db.close()

        return f"✅ You have successfully checked out from room {room_number}. We hope you enjoyed your stay!"

    # ---------------- 4️⃣ FAQ / facilities / timings ----------------
    chain = RECEPTIONIST_PROMPT | llm
    response = chain.invoke({
        "message": message
    }).content

    db.close()
    return response
