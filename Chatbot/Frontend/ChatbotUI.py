import time
from dotenv import load_dotenv
import streamlit as st
import requests
import json
import os
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt

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
if "execution_times" not in st.session_state:
    st.session_state.execution_times = {"with_summary": [], "without_summary": []}
# Display welcome message when the app loads or a new session starts
if "has_greeted" not in st.session_state:
    st.session_state.has_greeted = False

# Helper function to start a new session
def start_new_session():
    session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    st.session_state.current_session = session_id
    st.session_state.chat_sessions[session_id] = []

# Function to measure execution time
def measure_execution_time(payload):
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/user/query/", json=payload)
    execution_time = time.time() - start_time
    return response, execution_time


# Format the section for summarization
def clean_response(response):
    return response.replace("\n", " ")


def extract_latest_section(data, last_section):
    last_summary_index = -1
    for i in range(len(data) - 1, -1, -1):
        if data[i]["response"].startswith("Here's the summary of our session:"):
            last_summary_index = i
            break

    extracted_section = [
        msg for msg in data[last_summary_index + 1:]
        if not msg["response"].startswith("Here's the summary of our session:")
    ]
    if not extracted_section and last_section:
        return last_section
    return extracted_section

# Execution time comparison logic refactored
def execute_comparison(latest_query, recent_chat_context, recent_chat_context_without_summary):
    # Initialize lists to store results for plotting
    exec_time_with_summary = []
    exec_time_without_summary = []
    input_tokens_with_summary = []
    output_tokens_with_summary = []
    input_tokens_without_summary = []
    output_tokens_without_summary = []

    # With Summary Context
    payload_with_summary = {
        "queryResponse": latest_query,
        "sumContext": st.session_state.summary if "summary" in st.session_state else None,
        "isComparedExecution": True,
        "recentChatContext": recent_chat_context if recent_chat_context else None,
    }
    response_with_summary, time_with_summary = measure_execution_time(payload_with_summary)
    exec_time_with_summary.append(time_with_summary)
    if response_with_summary.status_code == 200:
        data = response_with_summary.json()
        input_tokens_with_summary.append(data.get("input_tokens", 0))
        output_tokens_with_summary.append(data.get("output_tokens", 0))

    # Without Summary Context
    payload_without_summary = {
        "queryResponse": latest_query,
        "isComparedExecution": True,
        "recentChatContext": recent_chat_context_without_summary if recent_chat_context_without_summary else None,
    }
    response_without_summary, time_without_summary = measure_execution_time(payload_without_summary)
    exec_time_without_summary.append(time_without_summary)
    if response_without_summary.status_code == 200:
        data = response_without_summary.json()
        input_tokens_without_summary.append(data.get("input_tokens", 0))
        output_tokens_without_summary.append(data.get("output_tokens", 0))

    return {
        "exec_time_with_summary": exec_time_with_summary,
        "exec_time_without_summary": exec_time_without_summary,
        "input_tokens_with_summary": input_tokens_with_summary,
        "output_tokens_with_summary": output_tokens_with_summary,
        "input_tokens_without_summary": input_tokens_without_summary,
        "output_tokens_without_summary": output_tokens_without_summary,
    }

from io import BytesIO

def plot_comparison_results(comparison_data, query_index):
    # Create Execution Time Line Graph
    fig_exec_time = plt.figure(figsize=(8, 5))
    plt.plot(query_index, comparison_data["exec_time_with_summary"], label="With Summary", marker="o")
    plt.plot(query_index, comparison_data["exec_time_without_summary"], label="Without Summary", marker="o")
    plt.xlabel("Query Index")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Execution Time Comparison")
    plt.legend()
    plt.grid()

    # Save fig_exec_time as an image
    buf_exec_time = BytesIO()
    fig_exec_time.savefig(buf_exec_time, format='png')
    buf_exec_time.seek(0)

    # Create Token Count Line Graph
    fig_token_count = plt.figure(figsize=(8, 5))
    plt.plot(query_index, comparison_data["input_tokens_with_summary"], label="Input Tokens With Summary", marker="o")
    plt.plot(query_index, comparison_data["output_tokens_with_summary"], label="Output Tokens With Summary", marker="o")
    plt.plot(query_index, comparison_data["input_tokens_without_summary"], label="Input Tokens Without Summary", marker="o")
    plt.plot(query_index, comparison_data["output_tokens_without_summary"], label="Output Tokens Without Summary", marker="o")
    plt.xlabel("Query Index")
    plt.ylabel("Token Count")
    plt.title("Token Count Comparison")
    plt.legend()
    plt.grid()

    # Save fig_token_count as an image
    buf_token_count = BytesIO()
    fig_token_count.savefig(buf_token_count, format='png')
    buf_token_count.seek(0)

    return buf_exec_time, buf_token_count


# Home menu
if not st.session_state.has_greeted and not st.session_state.current_session:
    st.markdown("## Welcome to the Chatbot Interface! 🤖")
    st.markdown(
        """
        <ul style="font-size: 20px; list-style-type: none; padding-left: 0;">
            <li>👉 Start a new session or select an existing one to continue.</li>
            <li>👉 You can upload PDF files, save your chat history, or summarize the current session.</li>
            <li>👉 Use the sidebar for session controls and other features.</li>
            <li>👉 A small comparison on the summarization as context vs non-summarization can be found by enabling execution time and pressing display current comparison 📊</li>
            <li>👉 Start a new session to begin the conversation. Enjoy! 🌟</li>
        </ul>
        """,
        unsafe_allow_html=True
    )
    st.session_state.has_greeted = True

# Sidebar for session management
st.sidebar.title("Chat Sessions")
if st.sidebar.button("Start New Session"):
    start_new_session()
    st.session_state.has_greeted = False
    successMess = st.success(f"New session started: {st.session_state.current_session}")
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

# Section to display notifications
if "notification_message" in st.session_state and st.session_state.notification_message:
    st.success(st.session_state.notification_message)
    # Clear the notification after displaying
    st.session_state.notification_message = None

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
                        st.session_state.notification_message = (
                            f"{result.get('file', uploaded_file.name)}: {result.get('status', 'Uploaded successfully')}"
                        )
                        st.experimental_rerun()  # Force a rerun to display the notification
                    else:
                        st.error(
                            f"Failed to upload {uploaded_file.name}: {response.text}"
                        )
                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("No files were selected for upload.")

# Execution time comparison
with st.sidebar.expander("Compare Execution Times"):
    compare_execution = st.checkbox("Enable Execution Time Comparison")

# Save Current Chat Session to a File and Mongodb
if st.sidebar.button("Save Current Session"):
    if st.session_state.current_session:
        session_data = st.session_state.chat_sessions.get(st.session_state.current_session, [])

        # Filter non-serializable objects and unwanted messages
        serializable_session_data = []
        for message in session_data:
            # Exclude messages that are summaries
            if "response" in message and message["response"].startswith("Here's the summary of our session:"):
                continue

            # Exclude messages containing specific keywords like "Execution Time Comparison"
            if "response" in message and "Execution Time Comparison" in message["response"]:
                continue

            # Create a copy of the message to filter non-serializable objects
            serializable_message = message.copy()

            # Remove non-serializable objects like 'plot'
            if "plot" in serializable_message:
                del serializable_message["plot"]

            # Append only filtered messages
            serializable_session_data.append(serializable_message)

        if serializable_session_data:
            # Save the session data as JSON
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_folder = os.path.join(current_dir, "..")
            chatlog_folder = os.path.join(base_folder, "Chatlog")
            os.makedirs(chatlog_folder, exist_ok=True)
            session_file_name = os.path.join(chatlog_folder, f"{st.session_state.current_session}.json")

            with open(session_file_name, "w") as f:
                json.dump(serializable_session_data, f, indent=4)

            # Save to MongoDB
            response = requests.post(
                f"{BASE_URL}/api/user/saveChatHistoryBySession/{st.session_state.current_session}",
                json={"message": serializable_session_data}
            )
            if response.status_code == 200:
                st.success("Chat session saved successfully to FastAPI.")
            else:
                st.error(f"Failed to save chat session. Error: {response.text}")
        else:
            warnMess = st.warning("No chat history to save.")
            time.sleep(3)
            warnMess.empty()


# Summarize current chat session
if st.session_state.current_session:
    if st.sidebar.button("Summarize Current Section"):
        session_id = st.session_state.current_session
        session_data = st.session_state.chat_sessions.get(session_id, [])

        last_section_data = st.session_state.get("last_section_data", [])
        current_section = extract_latest_section(session_data, last_section_data)

        # Check summary index
        # Identify all indices of summaries
        summary_indices = [
            idx for idx, msg in enumerate(session_data)
            if msg["response"].startswith("Here's the summary of our session:")
        ]

        # Determine the summarization range
        if not summary_indices:
            # No summaries exist yet; summarize from the beginning
            start_index = 0
        elif len(summary_indices) == 1:
            # One summary exists; summarize everything after it
            start_index = summary_indices[-1] + 1
        else:
            # Multiple summaries exist; summarize messages between the last two summaries
            start_index = summary_indices[-2] + 1


        if current_section != last_section_data:
            st.session_state["last_section_data"] = current_section

        if not current_section:
            st.warning("No dialog to summarize.")
        else:
            chat_history = " ".join([
                f"{msg['role'].capitalize()}: {clean_response(msg['response'])}"
                for msg in current_section
            ])
            if chat_history:
                response_summary = requests.post(
                    f"{BASE_URL}/api/user/summarizeChat/{session_id}",
                    json={"sessionHistoryLog": chat_history}
                )

                if response_summary.status_code == 200:
                    summary = response_summary.json().get("summary", "No summary returned")
                    st.session_state.summary = summary
                    st.session_state.chat_sessions[st.session_state.current_session].append(
                        {"role": "chatbot", "response": f"Here's the summary of our session:\n{summary}"}
                    )
                    # Save the last summarized index
                    st.session_state.last_summary_index[session_id] = len(session_data) - 1
                    # Save the first summary index if not already set
                    if f"{session_id}_first" not in st.session_state.last_summary_index:
                        st.session_state.last_summary_index[f"{session_id}_first"] = start_index

                    # Save the summary to MongoDB
                    response_saved_summary = requests.post(
                        f"{BASE_URL}/api/user/saveChatSummaryBySession/{session_id}",
                        json={"summary": summary}
                    )
                    if response_saved_summary.status_code == 200:
                        st.success("Chat session summary saved successfully to FastAPI.")
                    else:
                        st.error(f"Failed to save chat session summary. Error: {response_saved_summary.text}")
                else:
                    st.error(f"Failed to generate summary. Error: {response_summary.text}")
            else:
                st.warning("No new messages to summarize.")

# Measure execution times if comparison is enabled
if st.sidebar.button("Display Execution Comparison"):
    if compare_execution:
        if st.session_state.current_session:
            if "summary" not in st.session_state or not st.session_state.summary:
                st.error("No summary exists yet. Please summarize the session first before comparing execution times.")
            else:
                session_data = st.session_state.chat_sessions.get(st.session_state.current_session, [])
                user_prompts = [msg["response"] for msg in session_data if msg["role"] == "user"]

                if user_prompts:
                    latest_query_index = len(user_prompts) - 1
                    latest_query = user_prompts[latest_query_index]

                    # Extract the current chat section for comparison
                    last_section_data = st.session_state.get("last_section_data", [])
                    current_section = extract_latest_section(
                        session_data, last_section_data
                    )
                    recent_chat_context = {
                        "message": [
                            {"role": msg["role"], "response": clean_response(msg["response"])}
                            for msg in current_section
                        ]
                    }
                    # Filter non-serializable objects and unwanted messages
                    serializable_session_data = []
                    for message in session_data:
                        # Exclude messages that are summaries
                        if "response" in message and message["response"].startswith("Here's the summary of our session:"):
                            continue

                        # Exclude messages containing specific keywords like "Execution Time Comparison"
                        if "response" in message and "Execution Time Comparison" in message["response"]:
                            continue

                        # Create a copy of the message to filter non-serializable objects
                        serializable_message = message.copy()

                        # Remove non-serializable objects like 'plot'
                        if "plot" in serializable_message:
                            del serializable_message["plot"]

                        # Append only filtered messages
                        serializable_session_data.append(serializable_message)

                    recent_chat_context_without_summary = {"message": serializable_session_data}

                    # Perform execution comparison
                    comparison_results = execute_comparison(
                        latest_query, recent_chat_context, recent_chat_context_without_summary
                    )

                    # Generate plots
                    fig_exec_time, fig_token_count = plot_comparison_results(
                        comparison_results, [latest_query_index]
                    )

                    # Append comparison results to chat history
                    comparison_response = (
                        f"**Comparison Results:**\n\n"
                        f"- **With Summary Context:**\n"
                        f"  - Execution Time: {comparison_results['exec_time_with_summary'][0]:.2f} seconds\n"
                        f"  - Input Tokens: {comparison_results['input_tokens_with_summary'][0]}\n"
                        f"  - Output Tokens: {comparison_results['output_tokens_with_summary'][0]}\n\n"
                        f"- **Without Summary Context:**\n"
                        f"  - Execution Time: {comparison_results['exec_time_without_summary'][0]:.2f} seconds\n"
                        f"  - Input Tokens: {comparison_results['input_tokens_without_summary'][0]}\n"
                        f"  - Output Tokens: {comparison_results['output_tokens_without_summary'][0]}"
                    )
                    st.session_state.chat_sessions[st.session_state.current_session].append(
                        {
                            "role": "chatbot",
                            "response": comparison_response,
                            "plot_exec_time": fig_exec_time,
                            "plot_token_count": fig_token_count,
                        }
                    )
        else:
            st.warning("No user queries found to display comparison.")
    else:
        st.warning("No session data available for comparison.")
else:
    st.error("Enable Execution Time Comparison to use this feature.")


# Chatbot interaction session
if st.session_state.current_session:
    st.header("Ask a Question")

    # Display chat history for the current session
    for message in st.session_state.chat_sessions[st.session_state.current_session]:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["response"])
        elif message["role"] == "chatbot":
            with st.chat_message("assistant"):
                st.markdown(message["response"])
                if "plot_exec_time" in message:
                    st.image(message["plot_exec_time"], caption="Execution Time Comparison")
                if "plot_token_count" in message:
                    st.image(message["plot_token_count"], caption="Token Count Comparison")

    # Chat input
    user_query = st.chat_input("Enter your question", key="user_input")

    # Session_data (for the whole chatlog)
    session_data = st.session_state.chat_sessions.get(st.session_state.current_session, [])
    # Extract the current section (a part of chatlog) using the same logic
    last_section_data = st.session_state.get("last_section_data", [])
    current_section = extract_latest_section(
        st.session_state.chat_sessions.get(st.session_state.current_session, []),
        last_section_data
    )

    if current_section != last_section_data:
        st.session_state["last_section_data"] = current_section

    if user_query:
        st.session_state.chat_sessions[st.session_state.current_session].append(
            {"role": "user", "response": user_query}
        )
        with st.chat_message("user"):
            st.markdown(user_query)

        # Reformat the chat context
        recent_chat_context = {
            "message": [
                {"role": msg["role"], "response": clean_response(msg["response"])}
                for msg in current_section
            ]
        }

        # Prepare payload based on whether execution time comparison is enabled
        payload = {
            "queryResponse": user_query,
            "sumContext": st.session_state.summary if "summary" in st.session_state else None,
            "isComparedExecution": False,
            "recentChatContext": recent_chat_context if recent_chat_context else None,
        }

        response = requests.post(f"{BASE_URL}/api/user/query/", json=payload)
        chatbot_response = response.json().get("response", "No response received")

        st.session_state.chat_sessions[st.session_state.current_session].append(
            {"role": "chatbot", "response": chatbot_response}
        )
        with st.chat_message("assistant"):
            st.markdown(chatbot_response)