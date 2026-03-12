# graph/workflow.py

from langgraph.graph import StateGraph, END

from graph.state import ResortState
from agents_LG.router_node import router_node
from agents_LG.restaurant_nodes import restaurant_node
from agents_LG.reception_nodes import receptionist_node

# OLD handler (bridge during migration)
from agents.room_service_agent import handle_room_service_query


# ---------------- Bridge node for old room service ----------------
def room_service_bridge_node(state: ResortState) -> ResortState:
    """
    Temporary bridge node that calls the old room service agent.
    """
    response = handle_room_service_query(
        state["user_message"],
        state["conversation_id"]
    )

    return {
        **state,
        "response": response
    }


# ---------------- Conditional Router ----------------
def route_by_intent(state: ResortState) -> str:
    intent = state.get("active_intent")

    if intent == "RESTAURANT":
        return "restaurant"

    if intent == "RECEPTION":
        return "reception"

    if intent == "ROOM_SERVICE":
        return "room_service"

    return "reception"  # safe fallback


# ---------------- Build Graph ----------------
def build_resort_graph():
    workflow = StateGraph(ResortState)

    workflow.add_node("router", router_node)
    workflow.add_node("restaurant", restaurant_node)
    workflow.add_node("reception", receptionist_node)
    workflow.add_node("room_service", room_service_bridge_node)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "restaurant": "restaurant",
            "reception": "reception",
            "room_service": "room_service"
        }
    )

    workflow.add_edge("restaurant", END)
    workflow.add_edge("reception", END)
    workflow.add_edge("room_service", END)

    return workflow.compile()


# Compile once at import time
resort_graph = build_resort_graph()