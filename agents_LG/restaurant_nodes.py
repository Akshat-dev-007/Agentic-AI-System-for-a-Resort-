# agents/restaurant_nodes.py
# agents_LG/restaurant_nodes.py

from datetime import datetime
import re

from db import SessionLocal
from models.menu import MenuItem
from models.order import Order, OrderItem
from graph.state import ResortState


# ---------------- Helper: normalize text ----------------
def normalize(text: str) -> str:
    return re.sub(r"[^a-z]", "", text.lower())


def restaurant_node(state: ResortState) -> ResortState:
    """
    LangGraph restaurant workflow node.
    Uses deterministic stage-based logic, preserving your original FSM.
    """
    db = SessionLocal()

    try:
        stage = state.get("stage")
        msg = state["user_message"].strip()

        # ---------------- 1️⃣ Start Order → Show Menu ----------------
        if stage is None:
            items = db.query(MenuItem).all()

            menu_text = "\n".join(
                f"- {item.name} (₹{item.price})"
                for item in items
            )

            return {
                **state,
                "stage": "awaiting_item",
                "response": (
                    "🍽️ **Here is our menu:**\n\n"
                    f"{menu_text}\n\n"
                    "👉 Please type the item name you want to order."
                )
            }

        # ---------------- 2️⃣ Capture Item (BETTER MATCHING) ----------------
        if stage == "awaiting_item":
            items = db.query(MenuItem).all()

            user_norm = normalize(msg)
            matched_item = None

            # 1) Exact normalized match first (best / safest)
            for item in items:
                if normalize(item.name) == user_norm:
                    matched_item = item
                    break

            # 2) Conservative fallback: user input fully contained in item name
            #    (better than allowing short item names to hijack longer ones)
            if not matched_item:
                for item in items:
                    item_norm = normalize(item.name)
                    if user_norm and user_norm in item_norm:
                        matched_item = item
                        break

            if not matched_item:
                return {
                    **state,
                    "response": "❌ I couldn't find that item. Please type one item exactly as shown in the menu."
                }

            return {
                **state,
                "item": matched_item.name,
                "price": float(matched_item.price),
                "stage": "awaiting_quantity",
                "response": f"How many servings of **{matched_item.name}** would you like?"
            }

        # ---------------- 3️⃣ Capture Quantity ----------------
        if stage == "awaiting_quantity":
            if not msg.isdigit() or int(msg) <= 0:
                return {
                    **state,
                    "response": "Please enter a valid quantity (e.g., 1 or 2)."
                }

            return {
                **state,
                "quantity": int(msg),
                "stage": "awaiting_room",
                "response": "Please provide your room number."
            }

        # ---------------- 4️⃣ Capture Room ----------------
        if stage == "awaiting_room":
            quantity = state.get("quantity", 0)
            price = state.get("price", 0.0)
            total = price * quantity

            return {
                **state,
                "room_number": msg,
                "stage": "awaiting_confirmation",
                "response": (
                    "🧾 **Order Summary**\n\n"
                    f"Item: {state.get('item')}\n"
                    f"Quantity: {quantity}\n"
                    f"Room: {msg}\n"
                    f"Total: ₹{total}\n\n"
                    "Reply **YES** to confirm or **NO** to cancel."
                )
            }

        # ---------------- 5️⃣ Confirmation → DB WRITE ----------------
        if stage == "awaiting_confirmation":
            if msg.lower() not in ["yes", "no"]:
                return {
                    **state,
                    "response": "Please reply YES to confirm or NO to cancel."
                }

            if msg.lower() == "no":
                return {
                    "conversation_id": state["conversation_id"],
                    "user_message": state["user_message"],
                    "response": "❌ Order cancelled.",
                    "active_intent": None,
                    "stage": None,
                    "history": [],
                    "completed": True
                }

            total_amount = state["price"] * state["quantity"]

            order = Order(
                room_number=state["room_number"],
                total_amount=total_amount,
                status="CONFIRMED",
                created_at=datetime.utcnow()
            )
            db.add(order)
            db.commit()
            db.refresh(order)

            order_item = OrderItem(
                order_id=order.id,
                item_name=state["item"],
                quantity=state["quantity"],
                price=state["price"]
            )
            db.add(order_item)
            db.commit()

            return {
                "conversation_id": state["conversation_id"],
                "user_message": state["user_message"],
                "response": (
                    "✅ **Order Confirmed!**\n\n"
                    f"Item: {state['item']}\n"
                    f"Quantity: {state['quantity']}\n"
                    f"Total Bill: ₹{total_amount}"
                ),
                "active_intent": None,
                "stage": None,
                "history": [],
                "completed": True
            }

        # ---------------- Fallback ----------------
        return {
            **state,
            "response": "⚠️ Something went wrong. Please start your order again."
        }

    finally:
        db.close()