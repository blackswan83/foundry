#!/bin/bash

# Nuraxi Elembic Demo Startup Script
# Starts both backend and frontend servers

echo "=================================="
echo "  Nuraxi Elembic Demo Prototype   "
echo "  KFSHRC - January 2026           "
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}Starting Backend Server...${NC}"
cd "$PROJECT_DIR/backend"

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Start backend in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}Backend started on http://localhost:8000${NC}"
echo "API Docs: http://localhost:8000/api/docs"
echo ""

# Give backend time to start
sleep 2

echo -e "${BLUE}Starting Frontend Server...${NC}"
cd "$PROJECT_DIR/frontend"

# Install Node dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi

# Start frontend
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend started on http://localhost:3000${NC}"
echo ""

echo "=================================="
echo -e "${GREEN}Demo is running!${NC}"
echo "=================================="
echo ""
echo "Access the demo at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Handle shutdown
trap "echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

# Wait for processes
wait
