from datetime import datetime
import re

from langchain_openai import ChatOpenAI
from db import SessionLocal
from models.menu import MenuItem
from models.order import Order, OrderItem
from memory.conversation_store import get_context, update_context, clear_context

# ---------------- LLM (fallback only) ----------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2
)

# ---------------- Helper: normalize text ----------------
def normalize(text: str) -> str:
    return re.sub(r"[^a-z]", "", text.lower())

# ---------------- Handler ----------------
def handle_restaurant_query(message: str, conversation_id: str) -> str:
    db = SessionLocal()
    context = get_context(conversation_id)
    stage = context.get("stage")
    msg = message.strip()

    # ---------------- 1️⃣ Start Order → Show Menu ----------------
    if stage is None:
        items = db.query(MenuItem).all()

        menu_text = "\n".join(
            f"- {item.name} (₹{item.price})"
            for item in items
        )

        update_context(conversation_id, {"stage": "awaiting_item"})
        db.close()

        return (
            "🍽️ **Here is our menu:**\n\n"
            f"{menu_text}\n\n"
            "👉 Please type the item name you want to order."
        )

    # ---------------- 2️⃣ Capture Item (FUZZY MATCH) ----------------
    if stage == "awaiting_item":
        items = db.query(MenuItem).all()

        user_norm = normalize(msg)
        matched_item = None

        for item in items:
            if normalize(item.name) in user_norm or user_norm in normalize(item.name):
                matched_item = item
                break

        if not matched_item:
            db.close()
            return "❌ I couldn't find that item. Please type one item exactly as shown in the menu."

        update_context(conversation_id, {
            "item": matched_item.name,
            "price": matched_item.price,
            "stage": "awaiting_quantity"
        })

        db.close()
        return f"How many servings of **{matched_item.name}** would you like?"

    # ---------------- 3️⃣ Capture Quantity ----------------
    if stage == "awaiting_quantity":
        if not msg.isdigit() or int(msg) <= 0:
            db.close()
            return "Please enter a valid quantity (e.g., 1 or 2)."

        update_context(conversation_id, {
            "quantity": int(msg),
            "stage": "awaiting_room"
        })

        db.close()
        return "Please provide your room number."

    # ---------------- 4️⃣ Capture Room ----------------
    if stage == "awaiting_room":
        update_context(conversation_id, {
            "room_number": msg,
            "stage": "awaiting_confirmation"
        })

        total = context["price"] * context["quantity"]
        db.close()

        return (
            "🧾 **Order Summary**\n\n"
            f"Item: {context['item']}\n"
            f"Quantity: {context['quantity']}\n"
            f"Room: {msg}\n"
            f"Total: ₹{total}\n\n"
            "Reply **YES** to confirm or **NO** to cancel."
        )

    # ---------------- 5️⃣ Confirmation → DB WRITE ----------------
    if stage == "awaiting_confirmation":
        if msg.lower() not in ["yes", "no"]:
            db.close()
            return "Please reply YES to confirm or NO to cancel."

        if msg.lower() == "no":
            clear_context(conversation_id)
            db.close()
            return "❌ Order cancelled."

        total_amount = context["price"] * context["quantity"]

        order = Order(
            room_number=context["room_number"],
            total_amount=total_amount,
            status="CONFIRMED",
            created_at=datetime.utcnow()
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        order_item = OrderItem(
            order_id=order.id,
            item_name=context["item"],
            quantity=context["quantity"],
            price=context["price"]
        )
        db.add(order_item)
        db.commit()

        db.close()
        clear_context(conversation_id)

        return (
            "✅ **Order Confirmed!**\n\n"
            f"Item: {context['item']}\n"
            f"Quantity: {context['quantity']}\n"
            f"Total Bill: ₹{total_amount}"
        )

    db.close()
    return "⚠️ Something went wrong. Please start your order again."
