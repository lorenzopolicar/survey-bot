# LLM Survey Bot

This repository contains a minimal proof of concept for an LLM powered survey bot. It is split into a Python backend using FastAPI and a React/TypeScript frontend.

The backend uses Langchain/LangGraph to orchestrate a conversational agent that guides participants through a survey. Responses are stored in a SQLite database and scored via the OpenAI API.

The frontend provides a modern interface built with React and Material UI. Participants chat with the bot through a clean conversation view while admins can add questions and generate share links via a management screen.

## Running the backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # add your OpenAI API key
uvicorn app.main:app --reload
```

## Running the frontend
```bash
cd frontend
npm install
npm start
```

This project is only a lightweight demo and not intended for production use.
