#!/bin/bash
# Start backend and frontend for the LLM Survey Bot
# Usage: ./start_services.sh
set -e

# Start the FastAPI backend
(cd backend && uvicorn app.main:app --reload) &
BACK_PID=$!

# Stop backend when this script exits
trap "kill $BACK_PID" EXIT

# Run the React frontend
cd frontend
npm start
