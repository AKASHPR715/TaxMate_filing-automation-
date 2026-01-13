#!/bin/bash
# Run a single batch of the TaxMate benchmark
# Usage: ./run_batch.sh <batch_number>

set -e  # Exit on error

# Configuration
BATCH_NUM=${1:-1}
PROFILES_PER_BATCH=100  # Full batches with Vertex AI!
MODEL="gemini-1.5-flash"  # Google Vertex AI (uses your $300 credits)
PROJECT_ROOT="$(cd ../.. && pwd)"
RESULTS_DIR="./results"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}TaxMate Benchmark - Batch ${BATCH_NUM}${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if .env exists and has API key
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please create .env file and add your OPENAI_API_KEY"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs) 2>/dev/null || true

# Check if using Vertex AI (Gemini models)
if [[ "$MODEL" == gemini-* ]] || [[ "$MODEL" == vertex/* ]]; then
    echo -e "${YELLOW}Using Google Vertex AI${NC}"
    
    # Check if gcloud is configured
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ Error: gcloud CLI not found${NC}"
        echo "Install: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Optionally set project from env
    if [ -n "$GOOGLE_CLOUD_PROJECT" ]; then
        gcloud config set project "$GOOGLE_CLOUD_PROJECT" 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ Vertex AI configured${NC}"
else
    echo -e "${YELLOW}Using OpenRouter/OpenAI${NC}"
    
    # Check for appropriate API key based on model
    if [[ "$MODEL" == gpt-* ]]; then
        if [ -z "$OPENAI_API_KEY" ]; then
            echo -e "${RED}❌ Error: OPENAI_API_KEY not set${NC}"
            exit 1
        fi
    else
        if [ -z "$OPENROUTER_API_KEY" ]; then
            echo -e "${RED}❌ Error: OPENROUTER_API_KEY not set${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ API key configured${NC}"
fi

# Create results directory
mkdir -p "$RESULTS_DIR"

# Run the benchmark
echo ""
echo -e "${YELLOW}Running Batch ${BATCH_NUM}...${NC}"
echo "  Profiles: ${PROFILES_PER_BATCH}"
echo "  Model: ${MODEL}"
echo ""

cd "$PROJECT_ROOT"
python3 experiments/execution/runner.py \
    --count $PROFILES_PER_BATCH \
    --model $MODEL

# Move results to batch_run/results with batch number
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LATEST_CSV=$(ls -t experiments/output/benchmark_*.csv | head -1)
LATEST_JSON=$(ls -t experiments/output/detailed_log_*.json | head -1)
LATEST_TXT=$(ls -t experiments/output/readable_log_*.txt | head -1)

if [ -f "$LATEST_CSV" ]; then
    cp "$LATEST_CSV" "experiments/batch_run/results/batch_${BATCH_NUM}_benchmark.csv"
    cp "$LATEST_JSON" "experiments/batch_run/results/batch_${BATCH_NUM}_detailed.json"
    cp "$LATEST_TXT" "experiments/batch_run/results/batch_${BATCH_NUM}_readable.txt"
    
    echo ""
    echo -e "${GREEN}✅ Batch ${BATCH_NUM} Complete!${NC}"
    echo -e "${GREEN}Results saved to: experiments/batch_run/results/${NC}"
    echo ""
    
    # Show quick stats
    echo "Quick Stats:"
    TOTAL_LINES=$(wc -l < "experiments/batch_run/results/batch_${BATCH_NUM}_benchmark.csv")
    PROFILES_DONE=$((TOTAL_LINES - 1))  # Subtract header
    echo "  Profiles processed: ${PROFILES_DONE}"
    echo ""
else
    echo -e "${RED}❌ Error: No results file found${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
