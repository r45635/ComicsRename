#!/bin/bash

# ComicsRename Launcher Script
# This script helps launch the ComicsRename application with proper environment setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ComicsRename Launcher${NC}"
echo "========================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo -e "${RED}❌ Error: Python 3.8+ required. Found: $python_version${NC}"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo -e "${GREEN}✅ Python version: $(python3 --version)${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/lib/python*/site-packages/PySide6" ] && [ ! -d "venv/lib/python*/site-packages/PySide6" ]; then
    echo -e "${YELLOW}📋 Installing dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo "You can create one from .env.example for ComicVine API access:"
    echo "cp .env.example .env"
    echo ""
fi

# Launch the application
echo -e "${GREEN}🎮 Launching ComicsRename...${NC}"
echo ""

python main.py
