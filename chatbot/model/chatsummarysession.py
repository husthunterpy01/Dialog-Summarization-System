from pydantic import BaseModel
class ChatSummarizeSession(BaseModel):
    summary: str