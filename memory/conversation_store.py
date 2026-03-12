# memory/conversation_store.py

import json
import os
from dotenv import load_dotenv
import redis

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_TTL_SECONDS = int(os.getenv("REDIS_TTL_SECONDS", 3600))

# Redis client (decode_responses=True returns strings instead of bytes)
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)


def _conversation_key(conversation_id: str) -> str:
    return f"resort:conversation:{conversation_id}"


def _default_context() -> dict:
    return {
        "history": "",
        "stage": None
    }


def get_context(conversation_id: str) -> dict:
    """
    Returns full context for a conversation from Redis.
    If not found, returns default context.
    """
    key = _conversation_key(conversation_id)
    data = redis_client.get(key)

    if not data:
        return _default_context()

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return _default_context()


def update_context(conversation_id: str, data: dict):
    """
    Updates conversation state variables (stage, item, quantity, etc.)
    Stores the full updated context back into Redis with TTL.
    """
    key = _conversation_key(conversation_id)

    current = get_context(conversation_id)
    current.update(data)

    redis_client.setex(
        key,
        REDIS_TTL_SECONDS,
        json.dumps(current)
    )


def append_history(conversation_id: str, role: str, message: str):
    """
    Appends a message to conversation history.
    """
    key = _conversation_key(conversation_id)

    current = get_context(conversation_id)

    if "history" not in current:
        current["history"] = ""

    current["history"] += f"{role}: {message}\n"

    redis_client.setex(
        key,
        REDIS_TTL_SECONDS,
        json.dumps(current)
    )


def clear_context(conversation_id: str):
    """
    Clears entire conversation from Redis.
    """
    key = _conversation_key(conversation_id)
    redis_client.delete(key)