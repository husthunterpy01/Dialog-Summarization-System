from dotenv import load_dotenv
import streamlit as st
import requests
import os

load_dotenv()

# FastAPI endpoint base URL
BASE_URL = os.getenv("CHAT_ENDPOINT") # Replace with your actual FastAPI server URL

# Upload PDF Section
st.header("Upload PDF Files")
uploaded_files = st.file_uploader("Choose PDF files to upload", accept_multiple_files=True, type=["pdf"])

if st.button("Upload PDFs"):
    if uploaded_files:
        files = [("files", (file.name, file, file.type)) for file in uploaded_files]
        response = requests.post(f"{BASE_URL}/api/user/upload_pdf/", files=files)

        if response.status_code == 200:
            results = response.json().get("results", [])
            for result in results:
                st.success(f"{result['file']}: {result['status']}")
        else:
            st.error(f"Failed to upload PDFs: {response.text}")

# Query Section
st.header("Ask a Question")
user_query = st.text_input("Enter your question")

if st.button("Submit Query"):
    if user_query:
        payload = {"queryResponse": user_query}
        response = requests.post(f"{BASE_URL}/api/user/query/", json=payload)

        if response.status_code == 200:
            chatbot_response = response.json().get("response", "No response received")
            st.success(f"Chatbot Response: {chatbot_response}")
        else:
            st.error(f"Failed to fetch response: {response.text}")
