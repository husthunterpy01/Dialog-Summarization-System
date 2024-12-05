import uvicorn
from Controller.ChatbotController import app

# Program execution
if __name__ == "main":
    uvicorn.run(app, host="0.0.0.0", port=8000)