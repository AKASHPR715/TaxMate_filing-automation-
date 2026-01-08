#!/bin/bash

# TaxMate Backend Server Startup Script
# Starts the FastAPI application with organized API routers
# Components:
#   - orchestrator_component: Tax extraction, calculation, and analysis
#   - form_extraction_component: Document upload and processing
#   - chat_component: WebSocket chat interface

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set the Python path to include the project root directory (for app module imports)
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Create necessary directories if they don't exist
mkdir -p "${SCRIPT_DIR}/logs"
mkdir -p "${SCRIPT_DIR}/app/data/extracted"
mkdir -p "${SCRIPT_DIR}/app/data/uploads"
mkdir -p "${SCRIPT_DIR}/app/data/filing"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}Starting TaxMate Backend Server${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Check if virtual environment exists
if [ -d "${SCRIPT_DIR}/.venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source "${SCRIPT_DIR}/.venv/bin/activate"
elif [ -d "${SCRIPT_DIR}/venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source "${SCRIPT_DIR}/venv/bin/activate"
else
    echo -e "${BLUE}No virtual environment found, using system Python${NC}"
fi

# Install requirements
if [ -f "${SCRIPT_DIR}/requirements.txt" ]; then
    echo -e "${GREEN}Installing requirements...${NC}"
    pip install -r "${SCRIPT_DIR}/requirements.txt"
fi

# Navigate to the project directory
cd "${SCRIPT_DIR}"

# Display server info
echo -e "${BLUE}Server URL: ${NC}http://localhost:8000"
echo -e "${BLUE}API Docs: ${NC}http://localhost:8000/docs"
echo ""

# Run the main application
echo -e "${GREEN}Launching FastAPI Application...${NC}"
echo ""

# Pass command line arguments to main.py
python3 app/main.py "$@"

# Capture exit status
EXIT_STATUS=$?

echo ""
echo -e "${BLUE}==========================================${NC}"
if [ $EXIT_STATUS -eq 0 ]; then
    echo -e "${GREEN}Server completed successfully${NC}"
else
    echo -e "${RED}Server exited with error code: $EXIT_STATUS${NC}"
fi
echo -e "${BLUE}==========================================${NC}"

exit $EXIT_STATUS
