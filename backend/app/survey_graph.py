import uuid
from typing import List, TypedDict, Any, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from langgraph.graph.message import add_messages, AnyMessage
from langchain_core.runnables import RunnableConfig
from app.prompts import (
    response_classifier_llm, 
    response_classifier_prompt, 
    question_generator_prompt, 
    extended_question_generator_prompt,
    answer_recorder_prompt,
    answer_recorder_llm
)
from app.llm import llm
from sqlalchemy.orm import Session
import app.models as models
from app.schemas import ResponseClasification, AnswerRecording, Question
from langgraph.checkpoint.memory import InMemorySaver
from app import crud

DEV = True
# Examples as default values
QUESTION_1 = Question(id="1", text="What is your name?", guidelines="Provide your full name. e.g. John Doe")
QUESTION_2 = Question(id="2", text="What is your age?", guidelines="Provide your age. e.g. 25")
QUESTION_3 = Question(id="3", text="What is your city?", guidelines="Provide your city. e.g. New York")
QUESTION_LIST = [QUESTION_1, QUESTION_2, QUESTION_3]
from app.database import SessionLocal
DB = SessionLocal()
LINK = models.SurveyLink(token="test")

class State(TypedDict):
    current_question: Question
    classification: ResponseClasification
    questions: List[Question]
    skipped: List[Question]
    answers: dict[str, Any]
    current_messages: Annotated[List[AnyMessage], add_messages]
    messages: Annotated[List[AnyMessage], add_messages]
    link_id: int
    dev: bool = False


# --- Node Functions ---

def classify_response(state: State) -> State:
    """Classify the response to the current question."""

    current_question = state["current_question"]
    question = current_question.text
    guidelines = current_question.guidelines
    response = response_classifier_llm.invoke(response_classifier_prompt.format(
        question=question,
        guidelines=guidelines,
        conversation_history=state["current_messages"]
    ))
    return {"classification": response, "messages": [AIMessage(content=f"The classification of the response is {response.classification}. {response.reason}")]}

def generate_question(state: State) -> State:
    """Generate a question based on the response guidelines."""
    """
    if state["dev"]:
        state["current_question"] = QUESTION_1
        state["questions"] = QUESTION_LIST
        state["skipped"] = []
        state["answers"] = {}
        state["current_messages"] = [HumanMessage(content="Can you clarify your question? Do you want full legal name with middle name or just first name?")]
        state["messages"] = []
        state["dev"] = False
    """
    current_question = state["current_question"]
    if current_question is None:
        state["current_messages"] = [AIMessage(content="Survey is finished. Thank you for your time!")]
        return state
    question = current_question.text
    guidelines = current_question.guidelines
    last_response = state["messages"][-1].content if state["messages"] else None
    question = llm.invoke(question_generator_prompt.format(
        question=question,
        guidelines=guidelines,
        last_response=last_response))
    return {
        "messages": [question],
        "current_messages": [question],
    }

def ask_more_details(state: State) -> State:
    """Ask the user for more details."""
    current_question = state["current_question"]
    question = current_question.text
    guidelines = current_question.guidelines
    new_question = llm.invoke(extended_question_generator_prompt.format(
        question=question,
        guidelines=guidelines,
        conversation_history=state["current_messages"]))
    return {
        "messages": [new_question], 
        "current_messages": [new_question],
    }


def record_answer(state: State) -> State:
    """Record the answer to the current question."""
    current_question = state["current_question"]
    question = current_question.text
    guidelines = current_question.guidelines
    questions = state["questions"]
    current_messages = state["current_messages"]
    answer = answer_recorder_llm.invoke(answer_recorder_prompt.format(
        question=question,
        guidelines=guidelines,
        conversation_history=current_messages))

    # record answer to the database
    crud.create_answer(
        db=DB,
        link_id=state["link_id"],
        question_id=current_question.id,
        text=answer.answer,
        score=answer.score
    )

    # clear the current messages
    state["current_messages"] = [RemoveMessage(id=message.id) for message in state["current_messages"]]

    # update the state
    state["answers"][current_question.id] = answer
    if questions:
        current_question = questions.pop(0)
        state["current_question"] = current_question
        state["questions"] = questions
    else:
        state["current_question"] = None
    return state

def skip_question(state: State) -> State:
    """Skip the current question."""
    questions = state["questions"]
    current_question = state["current_question"]
    state["skipped"].append(current_question)
    questions.append(current_question)
    current_question = questions.pop(0)
    state["current_question"] = current_question
    state["questions"] = questions
    return state

# --- Edge Functions ---

def classify_response_edge(state: State):
    """Classify the response to the current question."""
    classfication = state["classification"]
    if classfication.classification == "skipped":
        return "skipped"
    elif classfication.classification == "answered (high quality)":
        return "record_answer"
    elif classfication.classification == "answered (low quality)" or classfication.classification == "other":
        return "same_question"  

def start_edge(state: State):
    """Start the survey."""
    if state["messages"]:
        return "classify_response"
    else:
        return "start_survey"


# --- Workflow ---

workflow = StateGraph(State)

workflow.add_node("classify_response", classify_response)
workflow.add_node("generate_question", generate_question)
workflow.add_node("ask_more_details", ask_more_details)
workflow.add_node("record_answer", record_answer)
workflow.add_node("skip_question", skip_question)

workflow.add_conditional_edges(
    START,
    start_edge,
    {
        "start_survey": "generate_question",
        "classify_response": "classify_response"
    }
)
workflow.add_conditional_edges(
    "classify_response", 
    classify_response_edge,
    {
        "skipped": "skip_question",
        "record_answer": "record_answer",
        "same_question": "ask_more_details",
        "other": "ask_more_details"
    }
)
workflow.add_edge("skip_question", "generate_question")
workflow.add_edge("record_answer", "generate_question")
workflow.add_edge("generate_question", END)

memory = InMemorySaver()
survey_agent = workflow.compile(checkpointer=memory)

def start_survey(db: Session, link: models.SurveyLink, questions: List[models.Question]):
    """Run the survey graph with a user message."""
    # Convert SQLAlchemy models to Pydantic models
    pydantic_questions = [Question.from_orm(q) for q in questions]
    current_question = pydantic_questions.pop(0)
    print(pydantic_questions)
    
    initial_state = {
        "current_question": current_question,
        "questions": pydantic_questions,
        "skipped": [],
        "answers": {},
        "current_messages": [],
        "messages": [],
        "link_id": link.id
    }

    configurable = {
        "thread_id": link.token,
    }

    config = RunnableConfig(
        configurable=configurable,
        run_id=str(uuid.uuid4()),
    )
    
    kwargs = {
        "input": initial_state,
        "config": config
    }


    # Run the graph
    return survey_agent.invoke(**kwargs)
   
def send_message(link: models.SurveyLink, user_message: str):
    config = RunnableConfig(
        configurable={
            "thread_id": link.token,
        },
        run_id=str(uuid.uuid4()),
    )

    kwargs = {
        "input": {
            "current_messages": [HumanMessage(content=user_message)],
            "messages": [HumanMessage(content=user_message)],
        },
        "config": config
    }


    return survey_agent.invoke(**kwargs)
