from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InteractionBase(BaseModel):
    student_name: str
    tutor_phone: str
    status: str
    claude_response: dict

class InteractionCreate(InteractionBase):
    pass

class InteractionUpdate(InteractionBase):
    status: Optional[str]
    claude_response: Optional[dict]

class InteractionRead(InteractionBase):
    id: int
    timestamp: datetime