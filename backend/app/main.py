from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from typing import List
import os

# Load environment variables from .env file
load_dotenv()

from .database import SessionLocal, engine
from . import models, schemas, crud, scoring, survey_graph

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/questions", response_model=List[schemas.Question])
def read_questions(db: Session = Depends(get_db)):
    questions = crud.get_questions(db=db)
    return questions

@app.post("/api/questions", response_model=schemas.Question)
def create_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    return crud.create_question(db=db, question=question)

@app.post("/api/links", response_model=schemas.SurveyLink)
def create_link(db: Session = Depends(get_db)):
    return crud.create_link(db=db)

@app.get("/api/links/{token}", response_model=schemas.SurveyLink)
def read_link(token: str, db: Session = Depends(get_db)):
    db_link = crud.get_link(db=db, token=token)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return db_link

@app.post("/api/answers", response_model=schemas.Answer)
def create_answer(answer: schemas.AnswerCreate, db: Session = Depends(get_db)):
    return crud.create_answer(
        db=db,
        link_id=answer.link_id,
        question_id=answer.question_id,
        text=answer.text,
        score=answer.score
    )

@app.get("/api/links/{link_id}/answers", response_model=List[schemas.Answer])
def read_answers_for_link(link_id: int, db: Session = Depends(get_db)):
    answers = crud.get_answers_for_link(db=db, link_id=link_id)
    return answers

@app.post("/api/links/{token}/start")
async def start_survey(token: str, db: Session = Depends(get_db)):
    link = crud.get_link(db, token)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    questions = crud.get_questions(db)
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found")
    
    # Start the survey and get the initial question
    initial_state = survey_graph.start_survey(db, link, questions)
    
    return {"response": initial_state["current_messages"][-1].content if initial_state["current_messages"] else None}

@app.post("/api/links/{token}/message")
async def send_message(token: str, message: schemas.ChatMessage, db: Session = Depends(get_db)):
    link = crud.get_link(db, token)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Send the message and get the response
    response_state = survey_graph.send_message(link, message.text)
    
    return {"response": response_state["current_messages"][-1].content if response_state["current_messages"] else None}
