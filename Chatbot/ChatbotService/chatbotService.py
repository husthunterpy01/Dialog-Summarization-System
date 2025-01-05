import os
from transformers import AutoTokenizer
from .vectordbHandlingService import get_query_results
from sentence_transformers import SentenceTransformer
from Chatbot.utils.LLMmodel_utils import LLM
from dotenv import load_dotenv

load_dotenv()
LLM_MODEL = os.getenv("LLM_MODEL")

# Load the sentence transformer model for the query
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
llama_chatbot = LLM(LLM_MODEL)
MAX_TOKEN = 10000
def generate_response(user_query,sum_context=None,recentChatContext=None, isCalculatedTokens = False):
    # Initialize token counts
    input_tokens_count = 0
    output_tokens_count = 0

    # Get embedding for the user's query
    query_embedding = model.encode([user_query])
    query_embedding = query_embedding.flatten().tolist()

    # Search the database for relevant document embeddings
    search_results = get_query_results(query_embedding,user_query,50,6)

    doc_context = truncate_search_results(search_results,MAX_TOKEN)
    prompt = """You are an AI assistant that answers questions based strictly on the provided context. You must do the following: 
            1. Carefully read the context provided.
            2. Answer the user's question only if the answer is explicitly present in the context.
            3. If the answer is not in the context or the context is insufficient, respond with: "I cannot help you with this question. Please contact the customer service for more information"
            4. You MUST keep your response as concise and short as possible
            5. At the end of your response, you MUST ask if user have any more questions, otherwise end the conversation politely. 
            """
    prompt += f"\n\n User Question:\n'{user_query}' \n\n"
    # if recentChat_context:
    #     prompt += f"Recent Chat Context:\n'{recentChat_context}'\n\n"
    if sum_context:
        prompt += f"Our context contain three parts:\n\n"
        prompt += f"Summary Context:\n'{sum_context}'\n\n"
    else:
        prompt += f"Our context contain two parts:\n\n"

    prompt += f"Recent Chat log context:\n'{recentChatContext}'\n\n"
    prompt += f"Retrieved context:\n'{doc_context}'"

    if isCalculatedTokens:
        input_tokens_count = len(tokenizer.encode(prompt))

    llm_response = llama_chatbot.generate_response(prompt)

    # Build the response string
    response = llm_response
    if "User:" in response:
        response = response[:response.index("User:")]
    if "User Question:" in response:
        response = response[:response.index("User Question:")]
    if "User Response:" in response:
        response = response[:response.index("User Response:")]

    if isCalculatedTokens:
        output_tokens_count = len(tokenizer.encode(llm_response))

    return {
        "response": response,
        "input_tokens": input_tokens_count if isCalculatedTokens else None,
        "output_tokens": output_tokens_count if isCalculatedTokens else None,
    }


def truncate_search_results(search_results, max_chars=10000):
    context = ""
    char_count = 0

    for result in search_results:
        content = result.get("content", "")
        token_id = tokenizer(content)["input_ids"]
        if char_count + len(token_id) > max_chars:
            context += tokenizer.decode(token_id[:max_chars - len(token_id)])
            break
        context += content + "\n"
        char_count += len(token_id)

    return context

