from pydantic import BaseModel
class Chatmessage(BaseModel):
    role: str
    response : str