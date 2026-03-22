# agents/router_node.py

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from graph.state import ResortState

# Schema for structured output of intent router llm
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
- RECEPTION: general queries, check-in/out, facilities, room availability, room booking
- RESTAURANT: food menu, food ordering, billing
- ROOM_SERVICE: cleaning, laundry, extra amenities

User message:
"{message}"
""")


def router_node(state: ResortState) -> ResortState:
    """
    LangGraph router node.
    If an active intent already exists, preserve it (intent locking).
    Otherwise classify and set active_intent.
    """
    if state.get("active_intent") and state.get("stage"):
        return state

    result: IntentSchema = llm.invoke(
        router_prompt.format(message=state["user_message"])
    )

    return {
        **state, # using unpacking concept of dictionary
        "active_intent": result.intent
    }
    # other way of returning  
    # state['active_intent'] = result.intent
    # return state

