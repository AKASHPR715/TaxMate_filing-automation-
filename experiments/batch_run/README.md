# Batch Execution Setup - Complete! ✅

## Quick Start Guide

### Step 1: Add Your OpenAI API Key

Since `.env` is gitignored, create it manually:

```bash
cd experiments/batch_run
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-actual-key-here
OPENROUTER_API_KEY=
EOF
```

**Or** just copy your existing API key:
```bash
# If you already have OPENAI_API_KEY in main .env:
grep OPENAI_API_KEY ../../.env > .env
```

### Step 2: Run Batches

**Option A - Run All at Once** (recommended):
```bash
./run_all_batches.sh
```

**Option B - Run One at a Time**:
```bash
./run_batch.sh 1    # Batch 1
# ... review results ...
./run_batch.sh 2    # Batch 2
# ... etc
```

### Step 3: Merge \u0026 Analyze

```bash
python3 merge_results.py      # Combine all CSVs
python3 analyze_results.py    # Generate statistics
```

---

## What's in This Folder

```
batch_run/
├── README.md                 # This file
├── .env                      # ⚠️  You need to create this!
│
├── run_batch.sh             # Run single batch
├── run_all_batches.sh       # Run all 5 batches
│
├── merge_results.py         # Merge batch CSVs
├── analyze_results.py       # Generate statistics
│
└── results/                 # Output (auto-created)
    ├── batch_1_benchmark.csv
    ├── batch_1_detailed.json
    ├── batch_1_readable.txt
    ├── ... (batches 2-5)
    ├── final_benchmark_500.csv
    └── analysis_report.md
```

---

## Cost & Time

- **Model**: GPT-4o-mini ($0.15/1M input, $0.60/1M output)
- **Per Batch**: ~$1.50, ~5 minutes
- **Total (5 batches)**: ~$7.50, ~25-30 minutes

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `.env` file not found | Create it: `nano .env` then add `OPENAI_API_KEY=sk-...` |
| API key not set | Make sure `.env` has your actual key, not `your-api-key-here` |
| Rate limit error | Wait 60 seconds, re-run the failed batch |
| Out of credits | Add credits at platform.openai.com/billing |

---

## After Running

1. ✅ Check results: `cat results/final_benchmark_500.csv`
2. ✅ Review analysis: `cat results/analysis_report.md`
3. ✅ Update IEEE paper with real data from tables

---

**Everything is ready! Just add your API key and run.** 🚀
