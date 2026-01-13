#!/bin/bash
# One-command setup for Google Vertex AI

echo "========================================"
echo "Setting up Google Vertex AI"
echo "========================================"
echo ""

# Step 1: Install library
echo "Step 1/4: Installing Google Cloud AI Platform library..."
pip install --quiet google-cloud-aiplatform
echo "✅ Library installed"
echo ""

# Step 2: Authenticate
echo "Step 2/4: Authenticating with Google Cloud..."
echo "A browser will open - please login with your Google account"
sleep 2
gcloud auth application-default login
echo "✅ Authenticated"
echo ""

# Step 3: Check/Set project
echo "Step 3/4: Checking Google Cloud project..."
PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT" ]; then
    echo "No project set. Available projects:"
    gcloud projects list
    echo ""
    read -p "Enter your project ID: " PROJECT_ID
    gcloud config set project "$PROJECT_ID"
else
    echo "Current project: $PROJECT"
    read -p "Use this project? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        gcloud projects list
        read -p "Enter your project ID: " PROJECT_ID
        gcloud config set project "$PROJECT_ID"
    fi
fi
echo "✅ Project configured"
echo ""

# Step 4: Enable API
echo "Step 4/4: Enabling Vertex AI API..."
gcloud services enable aiplatform.googleapis.com --quiet
echo "✅ API enabled"
echo ""

# Test
echo "========================================"
echo "Testing setup..."
echo "========================================"
cd /home/akash.anil@acsiatech.com/TaxMate_filing-automation-
python3 -c "from experiments.execution.llm_client import ResearchLLM; llm=ResearchLLM('gemini-1.5-flash'); print('Test question: What is 2+2?'); print('Answer:', llm.predict('What is 2+2?'))"

echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "You're ready to run:"
echo "  cd experiments/batch_run"
echo "  ./run_all_batches.sh"
echo ""
echo "Estimated cost: ~\$0.50 from your \$300 credits"
echo "========================================"
