import os
from .vectordbHandlingService import get_query_results
from sentence_transformers import SentenceTransformer
from Chatbot.utils.LLMmodel_utils import LLM
from dotenv import load_dotenv

load_dotenv()
LLM_MODEL = os.getenv("LLM_MODEL")
# Load the sentence transformer model for the query
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def generate_response(user_query):
    # Get embedding for the user's query
    query_embedding = model.encode([user_query])
    query_embedding = query_embedding.flatten().tolist()

    # Search the database for relevant document embeddings
    search_results = get_query_results(query_embedding)

    context = "\n".join(result['content'] for result in search_results if "content" in result)
    prompt = f"Context: {search_results}\n\nQuestion: {user_query}\nAnswer:"

    llama_chatbot = LLM(LLM_MODEL)
    llm_response = llama_chatbot.generate_response(prompt)  # Store LLM response separately

    # Build the response string
    response = "Here's what I found from the database:\n"
    # for result in search_results:
    #     response += f"- {result['content']}\n"
    #
    # response += "\nLLM Response:\n"
    response += llm_response  # Append LLM response

    return response
