# TaxMate Research Experiment: User Guide

This directory contains the code for the "TaxMate" Neuro-Symbolic experiment. This experiment benchmarks the accuracy of standard Large Language Models (LLMs) against the Neuro-Symbolic TaxMate architecture in calculating Indian Income Tax (FY 2024-25).

## 1. Prerequisites

Ensure you are in the project root (`/home/akash.anil@acsiatech.com/TaxMate_filing-automation-`) and have the virtual environment activated.

### Environment Variables
To run the LLM Baselines (Zero-Shot and Chain-of-Thought), you need an OpenAI API Key.
Ensure your `.env` file (or environment) has:
```bash
OPENAI_API_KEY=sk-proj-...
```

## 2. Running the Experiment

The main entry point is `experiments/execution/runner.py`.

### Quick Dry Run (No API Costs)
To verify the setup without making calls to OpenAI:
```bash
python3 experiments/execution/runner.py --dry-run --count 5
```
*   **--dry-run**: Mocks LLM calls (returns random/heuristic numbers).
*   **--count 5**: Generates 5 random tax profiles.

### Full Benchmark (Real)
To run the actual experiment with `gpt-4o-mini`:
```bash
python3 experiments/execution/runner.py --count 50 --model gpt-4o-mini
```
*   **--model**: Specify the model to test (default: `gpt-4o-mini`).
*   **Time Estimate**: ~1-2 seconds per profile (dominated by API latency).

## 3. Understanding the Output

### Console Output
The script will print a progress bar and a final summary:
```text
Results Summary (50 samples):
Neuro-Symbolic Exact Match: 100.0%
```

### Data Artifacts
Results are saved to `experiments/output/` with a timestamp:
*   `benchmark_YYYYMMDD_HHMMSS.csv`: Contains the full details for each run.

**Columns in CSV:**
*   `profile_id`: Unique ID of the synthetic taxpayer.
*   `complexity`: Profile complexity (Simple/Medium/Complex).
*   `regime`: The target regime (Old/New) tested.
*   `ground_truth`: The scientifically calculated correct tax (Python logic).
*   `neuro_sym_tax`: The result from TaxMate's Orchestrator (Python logic).
*   `zero_shot_tax`: The result extracted from the LLM's raw text response.
*   `cot_tax`: The result extracted from the LLM's Chain-of-Thought response.
*   `*_error`: Absolute difference from Ground Truth.
*   `*_raw`: Raw text output from the LLM (useful for debugging hallucinations).

## 4. Components Checklist

*   **Data Generator** (`experiments/data_generation/`): Creates valid, privacy-safe synthetic profiles.
*   **Execution Engine** (`experiments/execution/`): Runs the A/B test.
*   **Adapter** (`experiments/execution/adapter.py`): Translates synthetic data into the format TaxMate expects.

## 5. Troubleshooting

**Import Errors**
If you see errors related to `llama_cloud_services` or `langchain_classic`, ignore them. The runner script mocks these dependencies because they are not required for the *computation* benchmark (we skip the PDF extraction phase).
