import time

from dotenv import load_dotenv
import streamlit as st
import requests
import json
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# FastAPI endpoint base URL
BASE_URL = os.getenv("CHAT_ENDPOINT")  # Replace with your actual FastAPI server URL

# Initialization
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}  # Stores all sessions and their chat history
if "current_session" not in st.session_state:
    st.session_state.current_session = None  # Tracks the current active session


# Helper function to start a new session
def start_new_session():
    session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    st.session_state.current_session = session_id
    st.session_state.chat_sessions[session_id] = []

# Sidebar for session management
st.sidebar.title("Chat Sessions")
if st.sidebar.button("Start New Session"):
    start_new_session()
    successMess = st.success(f"New session started: {st.session_state.current_session}")
    time.sleep(3)
    successMess.empty()

# Display existing sessions in the sidebar
existing_sessions = list(st.session_state.chat_sessions.keys())
if existing_sessions:
    selected_session = st.sidebar.radio(
        "Select a session", options=existing_sessions, index=existing_sessions.index(st.session_state.current_session)
    )
    if selected_session:
        st.session_state.current_session = selected_session

# Display current session in the sidebar
if st.session_state.current_session:
    st.sidebar.write(f"Current Session: {st.session_state.current_session}")

# Upload PDF Section
st.sidebar.markdown("---")  # Separator line for clarity
with st.sidebar.expander("Upload PDF File", expanded=False):
    uploaded_file = st.file_uploader("Choose a PDF file to upload", accept_multiple_files=True, type=["pdf"])

    if st.button("Upload PDF", key="upload_pdf_button"):
        if uploaded_file:
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post(f"{BASE_URL}/api/user/upload_pdf/", files=files)

            if response.status_code == 200:
                result = response.json().get("result", {})
                st.sidebar.success(f"{result.get('file', 'File')}: {result.get('status', 'Uploaded successfully')}")
            else:
                st.sidebar.error(f"Failed to upload PDF: {response.text}")

# Save Current Session to a File
if st.sidebar.button("Save Current Session"):
    if st.session_state.current_session:
        session_data = st.session_state.chat_sessions.get(st.session_state.current_session, [])
        if session_data:
            session_file_name = f"{st.session_state.current_session}.json"
            with open(session_file_name, "w") as f:
                json.dump(session_data, f, indent=4)

            # Provide download link for the file
            successMess = st.success(f"Chat session saved to {session_file_name}. You can download below.")
            time.sleep(3)
            successMess.empty()

            st.download_button(
                label="Download Session Chat Log",
                data=json.dumps(session_data, indent=4),
                file_name=session_file_name,
                mime="application/json",
            )
        else:
            warnMess = st.warning("No chat history to save.")
            time.sleep(3)
            warnMess.empty()
    else:
        errorMess = st.error("No active session to save.")
        time.sleep(3)
        errorMess.empty()


# Chatbot interaction session
# Redisplay chat history for the current session
if st.session_state.current_session and st.session_state.current_session in st.session_state.chat_sessions:
    st.header("Ask a Question")
    for message in st.session_state.chat_sessions[st.session_state.current_session]:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["response"])
        elif message["role"] == "chatbot":
            with st.chat_message("assistant"):
                st.markdown(message["response"])

st.header("Ask a Question")
user_query = st.chat_input("Enter your question", key="user_input")
if user_query:
    # Add the user query to the side
    with st.chat_message("user"):
        st.markdown(user_query)
    payload = {"queryResponse": user_query}
    response = requests.post(f"{BASE_URL}/api/user/query/", json=payload)
    if response.status_code == 200:
        chatbot_response = response.json().get("response", "No response received")
        with st.chat_message("assistant"):
            st.markdown(chatbot_response)

        # Save the interaction in the current session (.json saving)
        if st.session_state.current_session:
            st.session_state.chat_sessions[st.session_state.current_session].append({"role": "user", "response": user_query})
            st.session_state.chat_sessions[st.session_state.current_session].append({"role": "chatbot", "response":chatbot_response })


