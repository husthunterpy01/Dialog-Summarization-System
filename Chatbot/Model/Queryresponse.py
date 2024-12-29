from pydantic import BaseModel
from typing import Optional

class QueryResponse(BaseModel):
    queryResponse:str
    sumContext: Optional[str] = None