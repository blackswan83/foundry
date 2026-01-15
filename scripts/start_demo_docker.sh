#!/bin/bash

# Nuraxi Foundry Demo Startup Script (Docker)
# Starts both backend and frontend servers using Docker
# Uses Python 3.12 and Node.js 22 from Docker images

echo "=================================="
echo "  Nuraxi Foundry Demo Prototype   "
echo "  KFSHRC - January 2026           "
echo "  (Docker Mode)                    "
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo -e "${BLUE}Install Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Use 'docker compose' (v2) if available, otherwise 'docker-compose' (v1)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo -e "${BLUE}Building Docker images (first time may take a few minutes)...${NC}"
$DOCKER_COMPOSE build

echo ""
echo -e "${BLUE}Starting services...${NC}"
$DOCKER_COMPOSE up -d

# Wait a moment for services to start
sleep 3

# Check if services are running
if docker ps | grep -q nuraxi-backend && docker ps | grep -q nuraxi-frontend; then
    echo ""
    echo "=================================="
    echo -e "${GREEN}Demo is running!${NC}"
    echo "=================================="
    echo ""
    echo -e "${GREEN}Backend:${NC}  http://localhost:8000"
    echo -e "${GREEN}API Docs:${NC} http://localhost:8000/api/docs"
    echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
    echo ""
    echo -e "${YELLOW}View logs:${NC} docker-compose logs -f"
    echo -e "${YELLOW}Stop:${NC}     docker-compose down"
    echo ""
    echo "Press Ctrl+C to stop viewing logs (services will keep running)"
    echo "Run 'docker-compose down' to stop all services"
    echo ""
    
    # Show logs
    $DOCKER_COMPOSE logs -f
else
    echo -e "${RED}Error: Services failed to start${NC}"
    echo "Check logs with: docker-compose logs"
    $DOCKER_COMPOSE logs
    exit 1
fi
