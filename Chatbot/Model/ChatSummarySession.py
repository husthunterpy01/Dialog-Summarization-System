from pydantic import BaseModel
class ChatSummarizeSession(BaseModel):
    timestamp: str
    summary: str