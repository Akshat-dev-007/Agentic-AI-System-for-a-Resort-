# graph/state.py

from typing import Optional, TypedDict, List


class ResortState(TypedDict, total=False):
    # Core request metadata
    conversation_id: str
    user_message: str
    response: str

    # Routing / agent control
    active_intent: Optional[str]   # RECEPTION / RESTAURANT / ROOM_SERVICE
    stage: Optional[str]

    # Restaurant fields
    item: Optional[str]
    price: Optional[float]
    quantity: Optional[int]
    room_number: Optional[str]

    # Room service fields
    request_type: Optional[str]

    # Optional conversation history (for later use / debugging)
    history: List[str]

    # Control flags
    completed: bool