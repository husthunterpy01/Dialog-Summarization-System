import os
from fastapi import UploadFile, File, HTTPException, APIRouter
import shutil
from typing import List
from pyparsing import empty
from starlette.responses import JSONResponse
from Chatbot.ChatbotService import generate_response,process_pdf
from Chatbot.Model import QueryResponse
from Chatbot.ChatbotService.vectordbHandlingService import create_search_index
from Chatbot.utils.database import collection
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
            if collection.count_documents({}) is empty:
                create_search_index()

            results.append({"file": file.filename, "status": "Processed successfully"})
        except Exception as e:
            results.append({"file": file.filename, "status": f"Error: {str(e)}"})

    return JSONResponse(
        status_code=200,
        content={"results": results}
    )


