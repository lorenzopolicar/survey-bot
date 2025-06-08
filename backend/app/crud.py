from sqlalchemy.orm import Session
from . import models, schemas

import uuid

def create_question(db: Session, question: schemas.QuestionCreate):
    db_q = models.Question(text=question.text, guidelines=question.guidelines)
    db.add(db_q)
    db.commit()
    db.refresh(db_q)
    return db_q


def get_questions(db: Session):
    return db.query(models.Question).all()


def create_link(db: Session):
    token = str(uuid.uuid4())
    db_link = models.SurveyLink(token=token)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


def get_link(db: Session, token: str):
    return db.query(models.SurveyLink).filter(models.SurveyLink.token == token).first()


def create_answer(db: Session, link_id: int, question_id: int, text: str, score: int):
    db_answer = models.Answer(link_id=link_id, question_id=question_id, text=text, score=score)
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer


def get_answers_for_link(db: Session, link_id: int):
    return db.query(models.Answer).filter(models.Answer.link_id == link_id).all()
