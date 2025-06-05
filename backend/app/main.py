from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, schemas, crud, scoring

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/questions", response_model=schemas.QuestionOut)
def create_question(q: schemas.QuestionCreate, db: Session = Depends(get_db)):
    return crud.create_question(db, q)


@app.get("/questions", response_model=list[schemas.QuestionOut])
def list_questions(db: Session = Depends(get_db)):
    return crud.get_questions(db)


@app.post("/links")
def create_link(db: Session = Depends(get_db)):
    link = crud.create_link(db)
    return {"token": link.token}


@app.post("/links/{token}/answers/{question_id}", response_model=schemas.AnswerOut)
def submit_answer(token: str, question_id: int, ans: schemas.AnswerCreate, db: Session = Depends(get_db)):
    link = crud.get_link(db, token)
    if not link:
        raise HTTPException(status_code=404, detail="link not found")
    q = db.query(models.Question).get(question_id)
    if not q:
        raise HTTPException(status_code=404, detail="question not found")
    score = scoring.score_answer(q.text, ans.text, q.guideline)
    return crud.create_answer(db, link.id, question_id, ans.text, score)


@app.get("/links/{token}/answers")
def get_answers(token: str, db: Session = Depends(get_db)):
    link = crud.get_link(db, token)
    if not link:
        raise HTTPException(status_code=404, detail="link not found")
    return crud.get_answers_for_link(db, link.id)
