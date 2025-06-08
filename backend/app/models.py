from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    guidelines = Column(String, nullable=True)
    answers = relationship("Answer", back_populates="question")

class SurveyLink(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    link_id = Column(Integer, ForeignKey("links.id"))
    text = Column(String)
    score = Column(Integer)

    question = relationship("Question", back_populates="answers")
