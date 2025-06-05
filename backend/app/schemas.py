from pydantic import BaseModel
from typing import Optional

class QuestionCreate(BaseModel):
    text: str
    guideline: Optional[str] = None

class QuestionOut(BaseModel):
    id: int
    text: str
    guideline: Optional[str]

    class Config:
        orm_mode = True

class AnswerCreate(BaseModel):
    text: str

class AnswerOut(BaseModel):
    id: int
    question_id: int
    link_id: int
    text: str
    score: int

    class Config:
        orm_mode = True
