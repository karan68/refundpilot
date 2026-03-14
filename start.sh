#!/usr/bin/env bash
# RefundPilot — Fresh Start Script
# Deletes old DB, starts backend + frontend from scratch
# Usage: ./start.sh (Linux/Mac) or run the PowerShell version below

echo "🤖 RefundPilot — Fresh Start"
echo "================================"

# Kill old processes on ports 8001 and 5173
echo "🔄 Killing old processes..."
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
sleep 1

# Delete old database
echo "🗑️  Deleting old database..."
rm -f backend/refundpilot.db

# Start backend
echo "🚀 Starting backend on port 8001..."
cd backend
pip install -r requirements.txt -q 2>/dev/null
python -m uvicorn main:app --port 8001 &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 3
echo "✅ Backend running (PID: $BACKEND_PID)"

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm install --silent 2>/dev/null
node patch-rollup.cjs 2>/dev/null
npx vite --port 5173 &
FRONTEND_PID=$!
cd ..

sleep 2
echo ""
echo "================================"
echo "✅ RefundPilot is running!"
echo "   Backend:  http://localhost:8001"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop both servers."
wait
