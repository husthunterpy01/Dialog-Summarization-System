# api.py

from fastapi import FastAPI
from pydantic import BaseModel
from pdf_processor import process_pdf
from Chatbot.ChatbotService.chatbotService import generate_response
app = FastAPI()

class Query(BaseModel):
    user_query: str

@app.post("/query/")
async def query(query: Query):
    response = generate_response(query.user_query)
    return {"response": response}

@app.post("/upload_pdf/")
async def upload_pdf(file: bytes):
    with open(file, "wb") as f:
        f.write(file)

    # Process PDF and save embeddings
    #Example
    documents = process_pdf("temp.pdf")
    return {"message": "PDF processed and embeddings saved", "documents": len(documents)}

