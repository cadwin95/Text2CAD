#!/bin/bash

# Kill ports if running
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# Start Backend
echo "🚀 Starting Backend (FastAPI)..."
source .venv/bin/activate
# Run from root so 'backend' package is resolvable
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo "🚀 Starting Frontend (Vite)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Development environment started!"
echo "   - Backend: http://localhost:8000"
echo "   - Frontend: http://localhost:5173"
echo ""
echo "Press CTRL+C to stop."

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
