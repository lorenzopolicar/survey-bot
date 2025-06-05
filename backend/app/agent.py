from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool, initialize_agent

from . import crud, models
from sqlalchemy.orm import Session


def build_agent(db: Session, link: models.SurveyLink, questions: list[models.Question]):
    llm = ChatOpenAI(temperature=0)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def submit_answer(question_id: int, text: str):
        # placeholder scoring using llm
        return crud.create_answer(db, link.id, question_id, text, score=3)

    tools = [
        Tool(
            name="submit",
            func=lambda qid_text: submit_answer(*qid_text),
            description="Submit answer to question."
        )
    ]

    system_prompt = "You are a survey bot. Ask the user each question in order."
    agent = initialize_agent(tools, llm, agent="chat-zero-shot-react-description", memory=memory)
    memory.chat_memory.add_message(SystemMessage(content=system_prompt))

    # prime conversation with first question
    if questions:
        memory.chat_memory.add_message(SystemMessage(content=f"Question 1: {questions[0].text}"))
    return agent
