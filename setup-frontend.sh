#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Expense Tracker - Setup Script    ${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Warning: Node.js is not installed${NC}"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Node.js version: $(node --version)"
echo -e "${GREEN}✓${NC} npm version: $(npm --version)"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}Installing dependencies...${NC}"
    npm install
    echo ""
fi

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${BLUE}To start the frontend:${NC}"
echo -e "  cd frontend"
echo -e "  npm run dev"
echo ""
echo -e "${BLUE}The app will be available at:${NC}"
echo -e "  http://localhost:3000"
echo ""
echo -e "${YELLOW}Note: Make sure the backend is running on http://localhost:8000${NC}"
echo ""
