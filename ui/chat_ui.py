import sys
import os
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests

API_CHAT = "http://127.0.0.1:5000/chat"

st.set_page_config(page_title="Resort AI Assistant", layout="centered")
st.title("🏨 Resort AI Assistant")
st.caption("Stateful multi-agent resort chatbot powered by Flask + LangGraph + Redis")

# ---------------- Session State ----------------
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_intent" not in st.session_state:
    st.session_state.current_intent = None


# ---------------- Sidebar Controls ----------------
with st.sidebar:
    st.header("⚙️ Session Controls")

    if st.button("🆕 New Conversation", use_container_width=True):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.session_state.current_intent = None
        st.rerun()

    st.markdown("---")
    st.subheader("🧠 Session Info")

    st.write(
        f"**Conversation ID:** "
        f"{st.session_state.conversation_id if st.session_state.conversation_id else 'Not started'}"
    )

    st.write(
        f"**Current Agent:** "
        f"{st.session_state.current_intent if st.session_state.current_intent else 'Not assigned'}"
    )

    st.markdown("---")
    st.caption(f"Backend: `{API_CHAT}`")


# ---------------- Helpers ----------------
def safe_post(url, payload):
    try:
        res = requests.post(url, json=payload, timeout=30)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.ConnectionError:
        st.error("🚨 Cannot connect to backend. Make sure Flask is running on port 5000.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏳ Backend request timed out.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"⚠️ Backend returned an error: {e}")
        return None
    except Exception as e:
        st.error(f"🚨 Unexpected error: {e}")
        return None


def send_message(message: str):
    payload = {"message": message}

    # Only include conversation_id if already assigned
    if st.session_state.conversation_id:
        payload["conversation_id"] = st.session_state.conversation_id

    response = safe_post(API_CHAT, payload)
    if not response:
        return

    # Update session state from backend response
    st.session_state.conversation_id = response.get("conversation_id")
    st.session_state.current_intent = response.get("intent")

    # Save assistant message with optional metadata
    assistant_reply = response.get("reply", "Sorry, I couldn't process that.")

    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_reply,
        "intent": response.get("intent")
    })

    # Render assistant message immediately
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

        if response.get("intent"):
            st.caption(f"🤖 Routed to: {response['intent']}")


# ---------------- Display Chat History ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and msg.get("intent"):
            st.caption(f"🤖 Routed to: {msg['intent']}")


# ---------------- Chat Input ----------------
user_input = st.chat_input("How can I help you today?")

if user_input:
    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Render user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send to backend
    send_message(user_input)