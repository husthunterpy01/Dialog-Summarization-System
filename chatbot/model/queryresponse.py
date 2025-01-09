from pydantic import BaseModel
from typing import Optional
from .chatlog import Chatlog
class QueryResponse(BaseModel):
    queryResponse:str
    sumContext: Optional[str] = None
    isComparedExecution: bool = False
    recentChatContext: Optional[Chatlog] = None

