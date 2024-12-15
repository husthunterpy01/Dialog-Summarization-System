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

    context = truncate_search_results(search_results)
    prompt = f"Context: {context}\n\nQuestion: {user_query}\nAnswer:"

    llama_chatbot = LLM(LLM_MODEL)
    llm_response = llama_chatbot.generate_response(prompt)

    # Build the response string
    response = "Here's what I found from the database:\n"
    #response += llm_response  # Append LLM response
    response += context
    return response



def truncate_search_results(search_results, max_chars=1500):
    context = ""
    char_count = 0

    for result in search_results:
        content = result.get("content", "")
        if char_count + len(content) > max_chars:
            break
        context += content + "\n"
        char_count += len(content)

    return context