from pydantic import BaseModel

class SummarizeChatRequest(BaseModel):
    sessionHistoryLog: str