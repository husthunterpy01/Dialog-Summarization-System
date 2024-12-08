# chatbot.py
import os
from .vectordbHandlingService import search_vectors
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama
from dotenv import load_dotenv

load_dotenv()
LLM_MODEL = os.getenv("LLM_MODEL")
# Load the sentence transformer model for the query
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def generate_response(user_query):
    # Get embedding for the user's query
    query_embedding = model.encode([user_query])

    # Search the database for relevant document embeddings
    search_results = search_vectors(query_embedding)

    context = "\n".join(search_results)
    prompt = f"Context: {search_results}\n\nQuestion: {user_query}\nAnswer:"

    llama_chatbot = Llama(LLM_MODEL)
    search_results = llama_chatbot.generate_response(prompt)

    # Process the results to generate a response (simple example here)
    response = "Here's what I found:\n"
    for result in search_results:
        response += f"{result['content']}\n"

    return response
