# chatbot.py
from vectordbHandlingService import search_vectors
from sentence_transformers import SentenceTransformer

# Load the sentence transformer model for the query
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def generate_response(user_query):
    # Get embedding for the user's query
    query_embedding = model.encode([user_query])

    # Search the database for relevant document embeddings
    search_results = search_vectors(query_embedding)

    # Process the results to generate a response (simple example here)
    response = "Here's what I found:\n"
    for result in search_results:
        response += f"{result['content']}\n"

    return response
