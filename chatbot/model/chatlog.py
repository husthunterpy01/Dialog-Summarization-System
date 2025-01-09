from pydantic import BaseModel
from chatbot.model.chatmessage import Chatmessage
from typing import List

class Chatlog(BaseModel):
    message: List[Chatmessage]
