from pydantic import BaseModel
from Chatbot.Model.ChatMessage import Chatmessage
from Chatbot.Model.ChatSummarySession import ChatSummarizeSession
from typing import List,Optional

class Chatlog(BaseModel):
    message: List[Chatmessage]
    summaries: Optional[List[ChatSummarizeSession]] = None