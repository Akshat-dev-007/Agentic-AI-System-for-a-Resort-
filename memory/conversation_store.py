# In-memory conversation store (can later be replaced with Redis)
conversation_store = {}

def get_context(conversation_id: str) -> dict:
    """
    Returns full context for a conversation.
    """
    return conversation_store.get(conversation_id, {
        "history": "",
        "stage": None
    })


def update_context(conversation_id: str, data: dict):
    """
    Updates conversation state variables (stage, item, quantity, etc.)
    """
    if conversation_id not in conversation_store:
        conversation_store[conversation_id] = {
            "history": "",
            "stage": None
        }

    conversation_store[conversation_id].update(data)


def append_history(conversation_id: str, role: str, message: str):
    """
    Appends a message to conversation history.
    """
    if conversation_id not in conversation_store:
        conversation_store[conversation_id] = {
            "history": "",
            "stage": None
        }

    conversation_store[conversation_id]["history"] += (
        f"{role}: {message}\n"
    )


def clear_context(conversation_id: str):
    """
    Clears entire conversation.
    """
    conversation_store.pop(conversation_id, None)
