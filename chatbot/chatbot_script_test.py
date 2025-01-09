from llama_cpp import Llama
import streamlit as st

class LLM:
    def __init__(self, model_path):
        # Load the model using llama_cpp
        self.model = Llama(model_path)

    def generate_response(self, prompt: str) -> str:
        try:
            # Generate a response based on the given prompt
            response = self.model(
                prompt,
                max_tokens=256,
                stop=["\n"],
                echo=False
            )
            # Get the raw output text
            raw_output = response.get('choices', [{}])[0].get('text', "").strip()
            if not raw_output:
                raw_output = "I'm sorry this knowledge hasn't been updated to me ? Can you ask another question ?"
            # Clean up any performance or additional logs from the raw output
            clean_output = self.clean_output(raw_output)

            return clean_output
        except Exception as e:
            return f"Error: {str(e)}"

    def clean_output(self, text: str) -> str:
        # Remove performance logging details
        lines = text.split("\n")
        cleaned_lines = [line for line in lines if not line.startswith("llama_perf_context_print")]

        # Further clean: Strip extra empty lines if there are any
        return "\n".join(cleaned_lines).strip()


# Initialize the LLM with the path to your Llama model
model_path = "/home/nhat/Dialog-Summarization-System/LLM_Model/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
llama_chatbot = LLM(model_path)

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

# If the user inputs something, generate a response
if user_input:
    # Generate the chatbot's response using llamacpp
    response = llama_chatbot.generate_response(user_input)

    # Append the user input and the chatbot response to the conversation history
    st.session_state.conversation.append(f"You: {user_input}")
    st.session_state.conversation.append(f"Chatbot: {response}")

# Display the conversation dynamically using a loop to simulate real-time interaction
with chat_placeholder.container():
    for message in st.session_state.conversation:
        if message.startswith("You:"):
            st.markdown(f"<div style='background-color:#E0F7FA;padding:10px;margin-bottom:5px;border-radius:5px;'>**You:** {message[4:]}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background-color:#F1F8E9;padding:10px;margin-bottom:5px;border-radius:5px;'>**Chatbot:** {message[9:]}</div>", unsafe_allow_html=True)

# Scrollable container for chat history
st.text_area("Chat History", "\n".join(st.session_state.conversation), height=400, max_chars=None, key="chat_history", disabled=True)
