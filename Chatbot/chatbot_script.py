from llama_cpp import Llama
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


import streamlit as st

# Initialize the LLM with the path to your Llama model
model_path = "/home/nhat/Dialog-Summarization-System/Chatbot/LLM_Model/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
llama_chatbot = LLM(model_path)

# Streamlit UI
st.title("LLM Chatbot")
st.write("Chat with the Llama model!")

# Initialize session state to keep track of chat history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# User input section
user_input = st.text_input("Your Question:")

# If the user inputs something
if user_input:
    # Generate the chatbot's response using llamacpp
    response = llama_chatbot.generate_response(user_input)

    # Append the user input and the chatbot response to the conversation history
    st.session_state.conversation.append(f"You: {user_input}")
    st.session_state.conversation.append(f"Chatbot: {response}")

# Display the chat history in a text area
chat_history = "\n".join(st.session_state.conversation)
st.text_area("Chat History", chat_history, height=400, max_chars=None, key="chat_history", disabled=True)

