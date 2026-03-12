# test_graph.py

from dotenv import load_dotenv
load_dotenv()

from graph.workflow import resort_graph

# Initial state (simulates persistent conversation state)
state = {
    "conversation_id": "test-123",
    "user_message": "I want to order food",
    "active_intent": None,
    "stage": None,
    "completed": False,
    "history": []
}

messages = [
    "I want to order food",
    "Butter Chicken",
    "2",
    "101",
    "YES"
]

for i, msg in enumerate(messages, start=1):
    state["user_message"] = msg
    result = resort_graph.invoke(state)

    print(f"\n=== TURN {i} ===")
    print(f"USER: {msg}")
    print(f"BOT: {result['response']}")
    print(f"STATE: active_intent={result.get('active_intent')}, stage={result.get('stage')}, completed={result.get('completed')}")

    # Persist state for next turn
    state = result