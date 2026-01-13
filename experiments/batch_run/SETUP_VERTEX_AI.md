# Google Vertex AI Setup Guide

## 🎯 Use Your $300 Google Cloud Credits!

**Cost for 500 profiles**: ~$0.50 (essentially FREE with your credits)

---

## Step 1: Install Required Libraries

```bash
pip install google-cloud-aiplatform
```

---

## Step 2: Authenticate with Google Cloud

```bash
# Login to your Google Cloud account
gcloud auth application-default login

# This will open a browser - login with your Google account
# that has the $300 credits
```

---

## Step 3: Set Your Project ID

```bash
# Find your project ID in Google Cloud Console
# Or list projects:
gcloud projects list

# Set the project
gcloud config set project YOUR-PROJECT-ID

# Example:
# gcloud config set project taxmate-research-12345
```

---

## Step 4: Enable Vertex AI API

```bash
gcloud services enable aiplatform.googleapis.com
```

---

## Step 5: Set Environment Variable (Optional)

```bash
# Add to experiments/batch_run/.env
echo "GOOGLE_CLOUD_PROJECT=your-project-id" >> experiments/batch_run/.env
```

Or the script will auto-detect from gcloud config!

---

## Step 6: Update Batch Run Configuration

**Edit `experiments/batch_run/run_batch.sh` (lines 9-10)**:

```bash
PROFILES_PER_BATCH=100  # Back to full batches!
MODEL="gemini-1.5-flash"  # Google Vertex AI model
```

---

## Step 7: Run Your Batches!

```bash
cd experiments/batch_run
./run_all_batches.sh
```

---

## 📊 Pricing Breakdown (with Vertex AI)

| Component | Tokens | Cost per 1M | Total Cost |
|-----------|--------|-------------|------------|
| Input (500 profiles) | ~1M tokens | $0.075 | $0.075 |
| Output (500 profiles) | ~350K tokens | $0.30 | $0.105 |
| **Total** | | | **~$0.18** |

**With safety margin**: ~$0.50 total

**Your credits**: $300.00 ✅

---

## Available Gemini Models

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| `gemini-1.5-flash` | **RECOMMENDED** - Balanced | Fast | Cheapest |
| `gemini-1.5-pro` | Complex reasoning | Medium | Medium |
| `gemini-2.0-flash-exp` | Experimental features | Fast | Free (rate limited) |

---

## Troubleshooting

### "Project not found"
```bash
gcloud config set project YOUR-PROJECT-ID
export GOOGLE_CLOUD_PROJECT=YOUR-PROJECT-ID
```

### "Permission denied"
```bash
gcloud auth application-default login
```

### "Vertex AI API not enabled"
```bash
gcloud services enable aiplatform.googleapis.com
```

---

## Quick Test

Test if everything works:

```bash
cd /home/akash.anil@acsiatech.com/TaxMate_filing-automation-
python3 -c "from experiments.execution.llm_client import ResearchLLM; llm=ResearchLLM('gemini-1.5-flash'); print(llm.predict('What is 2+2?'))"
```

Should output: "4" or similar response

---

**Ready to run! Follow the steps above, then execute `./run_all_batches.sh`** 🚀
