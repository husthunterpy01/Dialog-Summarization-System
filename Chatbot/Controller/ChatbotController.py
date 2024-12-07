import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
from pydantic import BaseModel
from PyPDF2 import PdfReader
from pdf_processor import process_pdf
from starlette.responses import JSONResponse
from streamlit import status
from Chatbot.ChatbotService.chatbotService import generate_response
from Chatbot.ChatbotService.textRetriverService import process_pdf
from Chatbot.Model import FilePath,QueryResponse
app = FastAPI()

@app.post("/user/query/")
async def query(query: QueryResponse):
    try:
        response = generate_response(query.user_query)
        return JSONResponse(
            status_code=200,
            content={"response": response}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/user/upload_pdf/")
async def upload_pdf(filepaths: List[FilePath]):
    for filepath in filepaths:
        if not os.getenv(filepath):
            raise HTTPException(status=400, detail="File path does not exist")

        if not filepath.filePath.endswith(".pdf"):
            raise HTTPException(status=400, detail={f"Uploaded is not the pdf file, please try again!"})

        # File processing
        try:
            document_processed = process_pdf(filepath)
            return JSONResponse(
                status_code=200,
                content={"message": "PDF processed successfully"}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


