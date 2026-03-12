# graph/workflow.py

from langgraph.graph import StateGraph, END

from graph.state import ResortState
from agents_LG.router_node import router_node
from agents_LG.restaurant_nodes import restaurant_node
from agents_LG.reception_nodes import receptionist_node
from agents_LG.room_service_nodes import room_service_node


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
    workflow.add_node("room_service", room_service_node)

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