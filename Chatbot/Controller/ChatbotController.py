import os
from fastapi import HTTPException, APIRouter
from typing import List
from starlette.responses import JSONResponse
from Chatbot.ChatbotService import generate_response,process_pdf
from Chatbot.Model import FilePath,QueryResponse
from Chatbot.ChatbotService.vectordbHandlingService import create_search_index
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
async def upload_pdf(filepaths: List[FilePath]):
        results = []
        for filepath in filepaths:
            file_path_str = str(filepath.filePath)
            if not os.path.exists(file_path_str):
                raise HTTPException(status_code=400, detail=f"File path {filepath.filePath} does not exist")

            if not filepath.filePath.endswith(".pdf"):
                raise HTTPException(status_code=400, detail=f"{filepath.filePath} is not a PDF file")

            try:
                process_pdf(file_path_str)
                create_search_index()
                results.append({"file": filepath.filePath, "status": "Processed successfully"})

            except Exception as e:
                results.append({"file": filepath.filePath, "status": f"Error: {str(e)}"})

        return JSONResponse(
            status_code=200,
            content={"results": results}
        )


