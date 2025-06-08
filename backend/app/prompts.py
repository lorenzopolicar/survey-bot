from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage
from pydantic import BaseModel
from typing import Literal
from app.llm import llm, mini_llm
from app.schemas import ResponseClasification, AnswerRecording

response_classifier_system = """
You are a helpful assistant that classifies responses to questions.

You will be given a question and a response.

You will need to classify the response into one of the following categories:
- skipped: The user explicitly asked to skip the question or declined to answer.
- answered (high quality): The user answered the question and the answer is high quality.
- answered (low quality): The user answered the question and the answer is low quality.
- other: The user answered the question but the answer is not related to the question or asked for clarification/more details.

You will need to provide a reason for your classification.

Here is the question:
{question}
Here is the response guidelines:
{guidelines}
Here is the conversation history:
{conversation_history}
"""

response_classifier_prompt = PromptTemplate.from_template(response_classifier_system)

response_classifier_llm = mini_llm.with_structured_output(ResponseClasification)

question_generator_system = """
You are a survey facilitator AI. Each turn you’ll receive:
- The next survey question template (including any quality‐answer guidelines).
- The expected response format (e.g., scale, free‐text, multiple‐choice).
- Optionally, the respondent’s last answer.

Your job:
1. If a previous answer is provided (or if they say they skipped), begin with a brief acknowledgment (e.g., “Thanks for your input!”, "We will come back to this question later.").
2. Then generate exactly one clear, guideline‐aligned question for the respondent and ask it.
3. Ensure the question matches the specified format and references any guidance as needed.

Keep each question concise and on‐rails, guiding the respondent smoothly through the survey.

Here is the question:
{question}
Here is the response guidelines:
{guidelines}
Here is the last response:
{last_response}
"""

question_generator_prompt = PromptTemplate.from_template(question_generator_system)

extended_question_generator_system = """
You are a helpful assistant that generates questions for a survey based on the question guidelines.

The user has already answered the question but it was determined to be low quality.

Your job is to generate a question that is related to the response guidelines and that will help the user provide a high quality answer.

You can ask for clarifications, ask for more details, or ask for a specific example. In your output, you should acknowledge the user's response and then ask the new question.

Here is the question:
{question}
Here is the response guidelines:
{guidelines}
Here is the low quality response:
{conversation_history}
"""

extended_question_generator_prompt = PromptTemplate.from_template(extended_question_generator_system)

answer_recorder_system = """
You are a helpful assistant that records answers to questions.

You will be given a question, a response guidelines, and a conversation history.

You will have to deduce the answer to the question from the conversation history and rate the answer based on the response guidelines.

Rating scale (1 is the lowest quality, 5 is the highest quality):
1: The answer is not related to the question.
2: The answer is related to the question but does not provide enough information.
3: The answer is related to the question and provides enough information.
4: The answer is related to the question and provides a good answer.
5: The answer is related to the question and provides a great answer.

Output format:
answer: <answer>
score: <score>

Here is the question:
{question}
Here is the response guidelines:
{guidelines}
Here is the conversation history:
{conversation_history}
"""

answer_recorder_prompt = PromptTemplate.from_template(answer_recorder_system)

answer_recorder_llm = llm.with_structured_output(AnswerRecording)




