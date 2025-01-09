from pydantic import BaseModel
from chatbot.model.ChatMessage import Chatmessage
from typing import List

class Chatlog(BaseModel):
    message: List[Chatmessage]
