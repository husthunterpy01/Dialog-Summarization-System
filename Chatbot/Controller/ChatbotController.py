import os
import shutil
from dotenv import load_dotenv
from fastapi import UploadFile, File, HTTPException, APIRouter
from typing import List
from starlette.responses import JSONResponse
from Chatbot.ChatbotService import generate_response,process_pdf
from Chatbot.Model import QueryResponse
from Chatbot.ChatbotService.vectordbHandlingService import create_vectorsearch_index,create_search_index
from Chatbot.utils.database import MongoDBClient
from Chatbot.Model.ChatLog import Chatlog
from Chatbot.Model.ChatSummarySession import ChatSummarizeSession
from Chatbot.ChatbotService.chatlogService import saveChatConversation, saveSummaryBySession
from Chatbot.ChatbotService.chatbotLogSummary import generate_summary

load_dotenv()
db_name = os.getenv("VECTOR_DB")
collection_name = os.getenv("VECTOR_DOCUMENT")

# Create an APIRouter instance for routes
router = APIRouter()

# This endpoint used for testing purpose only
@router.get("/")
async def root():
    return {"message": "Welcome to the Chatbot API"}

@router.post("/user/query/")
async def query(query: QueryResponse):
    try:
        response = generate_response(query.queryResponse)
        return JSONResponse(
            status_code=200,
            content={"response": response}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/user/upload_pdf/")
async def upload_pdf(files: List[UploadFile] = File(...)):
    results = []
    upload_folder = "./uploaded_pdfs"
    os.makedirs(upload_folder, exist_ok=True)

    for file in files:
        if not file.filename.endswith(".pdf"):
            results.append({"file": file.filename, "status": "Error: Not a PDF file"})
            continue

        try:
            # Save the uploaded file
            file_path = os.path.join(upload_folder, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            # Process the PDF
            process_pdf(file_path)

            if not MongoDBClient.list_search_indexes_checked(db_name, collection_name):
                create_vectorsearch_index()
                create_search_index()

            results.append({"file": file.filename, "status": "Processed successfully"})
        except Exception as e:
            results.append({"file": file.filename, "status": f"Error: {str(e)}"})

    return JSONResponse(
        status_code=200,
        content={"results": results}
    )

@router.post("user/summarizeChat/{session_id}")
async def summarizeChatSession(session_id: str, sessionHistoryLog: str):
    response = []
    try:
        generate_summary(sessionHistoryLog)
        response.append({"session_id":session_id, "status":"Save session successfully"})
    except Exception as e:
        response.append({"session_id":session_id, "status":"Save session fail"})

    return JSONResponse(
        status_code=200,
        content={"response": response}
    )

@router.post("user/saveChatHistoryBySession/{session_id}")
async def saveChatHistoryBySession(session_id: str, sessionHistory: Chatlog):
    response = []
    try:
        saveChatConversation(session_id, sessionHistory)
        response.append({"session_id":session_id, "status":"Save session successfully"})
    except Exception as e:
        response.append({"session_id":session_id, "status":"Save session fail"})

    return JSONResponse(
        status_code=200,
        content={"response": response}
    )

@router.post("user/saveChatSummaryBySession/{session_id}")
async def saveChatSummaryBySession(session_id: str, savedChatSummary: ChatSummarizeSession):
    response = []
    try:
        saveSummaryBySession(session_id, savedChatSummary)
        response.append({"session_id":session_id, "status":"Save summary session successfully"})
    except Exception as e:
        response.append({"session_id":session_id, "status":"Save summary session fail"})

    return JSONResponse(
        status_code=200,
        content={"response": response}
    )