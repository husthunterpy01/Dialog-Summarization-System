import time
from dotenv import load_dotenv
import streamlit as st
import requests
import json
import os
from datetime import datetime
import pandas as pd
# Load environment variables
load_dotenv()

# FastAPI endpoint base URL
BASE_URL = os.getenv("CHAT_ENDPOINT")  # Replace with your actual FastAPI server URL

# Initialization
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}  # Stores all sessions and their chat history
if "current_session" not in st.session_state:
    st.session_state.current_session = None  # Tracks the current active session
if "last_summary_index" not in st.session_state:
    st.session_state.last_summary_index = {}

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
    uploaded_files = st.file_uploader(
        "Choose PDF files to upload", accept_multiple_files=True, type=["pdf"]
    )

    if st.button("Upload PDF", key="upload_pdf_button"):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                files = {"files": (uploaded_file.name, uploaded_file, "application/pdf")}

                try:
                    # Send the POST request
                    response = requests.post(f"{BASE_URL}/api/user/upload_pdf/", files=files)

                    # Handle the response
                    if response.status_code == 200:
                        result = response.json().get("result", {})
                        st.sidebar.success(
                            f"{result.get('file', uploaded_file.name)}: {result.get('status', 'Uploaded successfully')}"
                        )
                    else:
                        st.sidebar.error(
                            f"Failed to upload {uploaded_file.name}: {response.text}"
                        )
                except requests.exceptions.RequestException as e:
                    st.sidebar.error(f"An error occurred: {e}")
        else:
            st.sidebar.warning("No files were selected for upload.")

# Summarize current chat session and save to mongodb
if st.session_state.current_session:
    if st.sidebar.button("Summarize Current Session"):
        session_id = st.session_state.current_session
        session_data = st.session_state.chat_sessions.get(session_id, [])

        # Function to extract the center part
        def extract_center(data):
            summary_indices = [
                i for i, msg in enumerate(data)
                if msg["response"].startswith("Here's the summary of our session:")
            ]

            if not summary_indices:
                # No summaries, return the entire session as center
                return data

            if len(summary_indices) == 1:
                # One summary, take everything before it as the center
                return data[:summary_indices[0]]

            # Multiple summaries
            # Skip consecutive summaries and take everything after the last one
            last_summary_index = summary_indices[-1]
            while last_summary_index + 1 < len(data) and data[last_summary_index + 1]["response"].startswith("Here's the summary of our session:"):
                last_summary_index += 1

            # Return everything after the last block of consecutive summaries
            return data[last_summary_index + 1:]

        # Extract the center part
        center_part = extract_center(session_data)

        # Format the center part for summarization
        def clean_response(response):
            return response.replace("\n", " ")

        chat_history = " ".join([
            f"{msg['role'].capitalize()}: {clean_response(msg['response'])}"
            for msg in center_part
        ])

        if chat_history:
            # Call the FastAPI endpoint to summarize the chat
            response_summary = requests.post(
                f"{BASE_URL}/api/user/summarizeChat/{session_id}",
                json={"sessionHistoryLog": chat_history}  # Send filtered history log as JSON
            )

            if response_summary.status_code == 200:
                summary = response_summary.json().get("summary", "No summary returned")
                st.session_state.summary = summary

                # Append the summary as a chatbot response
                st.session_state.chat_sessions[st.session_state.current_session].append(
                    {"role": "chatbot", "response": f"Here's the summary of our session:\n{summary}"}
                )

                # Save the index of the last summarized message
                st.session_state.last_summary_index[session_id] = len(session_data) - 1

                # Save the summary to session_id MongoDB
                response_saved_summary = requests.post(
                    f"{BASE_URL}/api/user/saveChatSummaryBySession/{session_id}",
                    json={"summary": summary}
                )
                if response_saved_summary.status_code == 200:
                    st.success("Chat session summary saved successfully to FastAPI.")
                else:
                    st.error(f"Failed to save chat session. Error: {response_saved_summary.text}")
            else:
                st.error(f"Failed to generate summary. Error: {response_summary.text}")
        else:
            st.warning("No new messages to summarize.")




# Save Current Chat Session to a File and Mongodb
if st.session_state.current_session:
    if st.sidebar.button("Save Current Session"):
        if st.session_state.current_session:
            session_data = st.session_state.chat_sessions.get(st.session_state.current_session, [])
            if session_data:
                session_file_name = f"{st.session_state.current_session}.json"
                with open(session_file_name, "w") as f:
                    json.dump(session_data, f, indent=4)

                # Save to mongodb
                session_id = st.session_state.current_session
                response = requests.post(
                    f"{BASE_URL}/api/user/saveChatHistoryBySession/{session_id}",
                    json={"message": session_data}
                )
                if response.status_code == 200:
                    st.success("Chat session saved successfully to FastAPI.")
                else:
                    st.error(f"Failed to save chat session. Error: {response.text}")

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


#Chat area
user_query = st.chat_input("Enter your question", key="user_input")
if user_query:
    # Add the user query to the side
    with st.chat_message("user"):
        st.markdown(user_query)

    if "summary" in st.session_state and st.session_state.summary:
        summary_context = st.session_state.summary
        payload = {"queryResponse": user_query, "summary_context": summary_context}
    else:
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




