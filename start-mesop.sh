#!/bin/bash

# Mesop UI Startup Script
# Starts the Mesop application server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Starting Mesop UI...${NC}"
echo ""

# Activate virtual environment
if [ ! -f ".venv/bin/activate" ]; then
    echo -e "${RED}✗ Virtual environment not found in .venv${NC}"
    echo -e "${YELLOW}  Please run ./setup-mesop.sh first${NC}"
    exit 1
fi

echo -e "${BLUE}Activating Python virtual environment...${NC}"
source .venv/bin/activate

echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Start the Mesop app
echo -e "${BLUE}Starting Mesop server...${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Mesop UI starting...${NC}"
echo ""
echo "  🔧 Mesop URL:   http://localhost:8080/home"
echo ""
echo "  Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the server from project root
cd mesop_app
python main.py
