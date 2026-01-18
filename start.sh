#!/bin/bash
# Ibn Battuta - Start Script
# Starts both backend and frontend

set -e

echo "🚀 Starting Ibn Battuta..."
echo ""

# Check if conda environment exists
if ! conda env list | grep -q "ibn_battuta"; then
    echo "❌ Conda environment 'ibn_battuta' not found!"
    echo "Please run ./setup_mac.sh first"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and add your API keys"
    exit 1
fi

echo "Starting backend server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start backend in background
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate ibn_battuta
python api.py &
BACKEND_PID=$!

echo ""
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Running on http://localhost:5000"
echo ""

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 3

echo "Starting frontend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start frontend
cd frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   Opening http://localhost:3000 in your browser..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✨ Ibn Battuta is running! ✨"
echo ""
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ Stopped"
    exit 0
}

trap cleanup INT TERM

# Wait for user interrupt
wait
