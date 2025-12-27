import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests

API_CHAT = "http://localhost:5000/chat"

st.set_page_config(page_title="Resort AI Assistant", layout="centered")
st.title("🏨 Resort AI Assistant")

# ---------------- Session State ----------------
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- Helpers ----------------
def safe_post(url, payload):
    try:
        res = requests.post(url, json=payload, timeout=30)
        res.raise_for_status()
        return res.json()
    except Exception:
        st.error("🚨 Backend unavailable. Please try again.")
        return None


def send_message(message: str):
    payload = {"message": message}

    if st.session_state.conversation_id:
        payload["conversation_id"] = st.session_state.conversation_id

    response = safe_post(API_CHAT, payload)
    if not response:
        return

    st.session_state.conversation_id = response["conversation_id"]

    st.session_state.messages.append({
        "role": "assistant",
        "content": response["reply"]
    })

    with st.chat_message("assistant"):
        st.markdown(response["reply"])


# ---------------- Display Chat History ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- Chat Input ----------------
user_input = st.chat_input("How can I help you today?")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    send_message(user_input)
