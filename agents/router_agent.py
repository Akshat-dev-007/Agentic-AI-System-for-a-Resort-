from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal

class IntentSchema(BaseModel):
    intent: Literal["RECEPTION", "RESTAURANT", "ROOM_SERVICE"] = Field(
        description="The department best suited to handle the user request"
    )

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
).with_structured_output(IntentSchema)


router_prompt = ChatPromptTemplate.from_template("""
You are an intelligent routing agent for a resort.

Classify the user message into exactly ONE of the following intents:
- RECEPTION: general queries, check-in/out, facilities, room availability
- RESTAURANT: food menu, food ordering, billing
- ROOM_SERVICE: cleaning, laundry, extra amenities

User message:
"{message}"
""")

from memory.conversation_store import get_context

def route_query(message: str, conversation_id: str) -> str:
    context = get_context(conversation_id)

    # 🔒 Lock intent during active flows
    if context.get("active_intent"):
        return context["active_intent"]

    result: IntentSchema = llm.invoke(
        router_prompt.format(message=message)
    )

    return result.intent

