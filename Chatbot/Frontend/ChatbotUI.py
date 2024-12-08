import streamlit as st
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CHAT_ENDPOINT = os.getenv("CHAT_ENDPOINT")
# Streamlit UI
st.title("LLM Chatbot")
st.write("Chat with the Llama model!")

# Initialize session state to keep track of chat history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# User input section
user_input = st.text_input("Your Question:", value=st.session_state.user_input, key="user_input")

# Create an empty placeholder for the chat interaction to simulate real-time conversation
chat_placeholder = st.empty()

if user_input:
    # Send the user query to the FastAPI endpoint
    try:
        response = requests.post(
            CHAT_ENDPOINT,
            json={"user_query": user_input}
        )
        response.raise_for_status()  # Raise an error for HTTP error codes
        chatbot_response = response.json().get("response", "Sorry, no response received.")

        # Append the user input and the chatbot response to the conversation history
        st.session_state.conversation.append(f"You: {user_input}")
        st.session_state.conversation.append(f"Chatbot: {chatbot_response}")

        # Clear the user input field
        st.session_state.user_input = ""

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {str(e)}")

# Display the conversation dynamically using a loop to simulate real-time interaction
with chat_placeholder.container():
    for message in st.session_state.conversation:
        if message.startswith("You:"):
            st.markdown(f"<div style='background-color:#E0F7FA;padding:10px;margin-bottom:5px;border-radius:5px;'>**You:** {message[4:]}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background-color:#F1F8E9;padding:10px;margin-bottom:5px;border-radius:5px;'>**Chatbot:** {message[9:]}</div>", unsafe_allow_html=True)

# Scrollable container for chat history
st.text_area("Chat History", "\n".join(st.session_state.conversation), height=400, max_chars=None, key="chat_history", disabled=True)