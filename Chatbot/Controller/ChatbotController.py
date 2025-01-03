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
from Chatbot.Model.ChatSummarizationRequest import SummarizeChatRequest
from Chatbot.Model.ChatLog import Chatlog
from Chatbot.Model.ChatSummarySession import ChatSummarizeSession
from Chatbot.ChatbotService.chatlogService import saveChatConversation, saveSummaryBySession,createSessionIdIndex
from Chatbot.ChatbotService.chatbotLogSummaryService import generate_summary

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
async def query(userprompt: QueryResponse):
    try:
        response = generate_response(userprompt.queryResponse, userprompt.sumContext)
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
            error_message = f"Error processing file {file.filename}: {str(e)}"
            raise HTTPException(status_code=500, detail=error_message)


    return JSONResponse(
            status_code=200,
            content={"results": results}
        )

@router.post("/user/summarizeChat/{session_id}")
async def summarizeChatSession(session_id: str, request: SummarizeChatRequest):
    try:
        # Extract the session history log from the request body
        session_history_log = request.sessionHistoryLog

        # Generate the summary using the provided history log
        summary = generate_summary(session_history_log)

        # Return the summary in the response
        return JSONResponse(
            status_code=200,
            content={
                "session_id": session_id,
                "status": "Summarization successful",
                "summary": summary
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize chat session: {str(e)}")

@router.post("/user/saveChatHistoryBySession/{session_id}")
async def saveChatHistoryBySession(session_id: str, sessionHistory: Chatlog):
    response = []
    try:
        createSessionIdIndex()
        saveChatConversation(session_id, sessionHistory)
        response.append({"session_id":session_id, "status":"Save session successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving chatlog: {str(e)}")

    return JSONResponse(
        status_code=200,
        content={"response": response}
    )

@router.post("/user/saveChatSummaryBySession/{session_id}")
async def saveChatSummaryBySession(session_id: str, savedChatSummary: ChatSummarizeSession):
    response = []
    try:
        createSessionIdIndex()
        saveSummaryBySession(session_id, savedChatSummary)
        response.append({"session_id":session_id, "status":"Save summary session successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save summary session fail: {str(e)}")

    return JSONResponse(
        status_code=200,
        content={"response": response}
    )