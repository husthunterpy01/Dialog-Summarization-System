import uvicorn
from fastapi import FastAPI
from chatbot.controller.chatbotcontroller import router as chatbot_router

# Initialize FastAPI app
app = FastAPI()

# Include the router
app.include_router(chatbot_router, prefix="/api", tags=["Chatbot"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
