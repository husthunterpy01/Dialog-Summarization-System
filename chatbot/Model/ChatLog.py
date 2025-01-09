from pydantic import BaseModel
from Chatbot.Model.ChatMessage import Chatmessage
from typing import List

class Chatlog(BaseModel):
    message: List[Chatmessage]
