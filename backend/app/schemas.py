from pydantic import BaseModel
from typing import Optional, Literal

class Question(BaseModel):
    id: int
    text: str
    guidelines: Optional[str]

    model_config = {
        "from_attributes": True
    }

class QuestionCreate(BaseModel):
    text: str
    guidelines: Optional[str]

class QuestionOut(BaseModel):
    id: int
    text: str
    guidelines: Optional[str]

class LinkOut(BaseModel):
    token: str

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

class ResponseClasification(BaseModel):
    classification: Literal["skipped", "answered (high quality)", "answered (low quality)", "other"]
    reason: str

class AnswerRecording(BaseModel):
    answer: str
    score: int

class ChatMessage(BaseModel):
    text: str

class SurveyLink(BaseModel):
    id: int
    token: str

class Answer(BaseModel):
    id: int
    question_id: int
    link_id: int
    text: str
    score: int

class AnswerCreate(BaseModel):
    text: str


