# Tax Benchmark Runner - Free LLM Guide

## 🆓 Using Free Models from OpenRouter

The benchmark now defaults to **100% FREE** models from OpenRouter! No credit card required for basic usage.

## Quick Start

### 1. Get Free OpenRouter API Key

```bash
# Visit: https://openrouter.ai/keys
# Create account and copy your API key (free tier is sufficient)
```

### 2. Set Environment Variable

```bash
# Add to your .env file
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx

# Or export directly
export OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
```

### 3. Run Benchmark

```bash
# Default: Uses free Gemini 2.0 Flash
python3 experiments/execution/runner.py --count 10

# Dry run (no API calls)
python3 experiments/execution/runner.py --count 5 --dry-run

# Use different free model
python3 experiments/execution/runner.py --count 20 --model google/gemini-flash-1.5:free

# Use Llama (smaller, faster)
python3 experiments/execution/runner.py --count 50 --model meta-llama/llama-3.2-3b-instruct:free
```

## 🎯 Recommended Free Models

### Best for Tax Calculations

| Model | Speed | Accuracy | Context | Notes |
|-------|-------|----------|---------|-------|
| **google/gemini-2.0-flash-exp:free** | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 1M tokens | **DEFAULT** - Best overall |
| google/gemini-flash-1.5:free | ⚡⚡ | ⭐⭐⭐⭐ | 1M tokens | Good balance |
| meta-llama/llama-3.2-3b-instruct:free | ⚡⚡⚡ | ⭐⭐⭐ | 128K tokens | Lightweight |

### Other Free Options

- `qwen/qwen-2-7b-instruct:free` - Chinese model, good at math
- `microsoft/phi-3-mini-128k-instruct:free` - Microsoft's small model
- `huggingfaceh4/zephyr-7b-beta:free` - Community favorite

## 💰 Paid Models (Optional)

If you need better accuracy, these are affordable:

- `openai/gpt-4o-mini` - $0.15/1M tokens (~$0.01 per 100 profiles)
- `openai/gpt-4o` - $5/1M tokens (~$0.30 per 100 profiles)
- `anthropic/claude-3.5-sonnet` - $3/1M tokens

## 📊 Typical Costs

### Free Tier (Gemini)
- **0 profiles**: $0.00 ✅
- **100 profiles**: $0.00 ✅
- **1000 profiles**: $0.00 ✅
- **Rate limit**: ~60 requests/minute

### GPT-4o-mini (Paid)
- **100 profiles**: ~$0.01
- **1000 profiles**: ~$0.10
- **10,000 profiles**: ~$1.00

## 🚀 Full Command Reference

```bash
# View all options
python3 experiments/execution/runner.py --help

# Small test with free model
python3 experiments/execution/runner.py --count 5

# Production benchmark (100 samples)
python3 experiments/execution/runner.py --count 100

# Large scale with paid model
python3 experiments/execution/runner.py --count 1000 --model openai/gpt-4o-mini

# Compare multiple models (run separately and compare CSV outputs)
python3 experiments/execution/runner.py --count 50 --model google/gemini-2.0-flash-exp:free
python3 experiments/execution/runner.py --count 50 --model meta-llama/llama-3.2-3b-instruct:free
python3 experiments/execution/runner.py --count 50 --model openai/gpt-4o-mini
```

## 📁 Output Files

Every run creates 4 files in `experiments/output/`:

1. **synthetic_profiles_*.json** - Input data for reproducibility
2. **benchmark_*.csv** - Quick results table
3. **detailed_log_*.json** - Complete results with prompts
4. **readable_log_*.txt** - Human-friendly report

## 🔍 Example Output

```
================================================================================
BENCHMARK RESULTS SUMMARY (50 samples)
================================================================================

Exact Match Accuracy (within ₹10):
  Neuro-Symbolic:     92.0%
  Zero-Shot LLM:      54.0%
  Chain-of-Thought:   68.0%

Average Error:
  Neuro-Symbolic:    ₹      245.50
  Zero-Shot LLM:     ₹    8,423.20
  Chain-of-Thought:  ₹    3,156.80
```

## 💡 Tips

1. **Start Small**: Test with `--count 5` first
2. **Use Dry Run**: Test your setup with `--dry-run` (mocks LLM calls)
3. **Free is Good**: Gemini 2.0 Flash is often as good as GPT-4o-mini
4. **Compare Models**: Run same profiles through different models
5. **Check Logs**: Review readable_log_*.txt for detailed analysis

## 🛠️ Troubleshooting

### "OPENROUTER_API_KEY not found"
```bash
# Make sure .env file exists in project root
echo "OPENROUTER_API_KEY=your-key-here" >> .env
```

### "Rate limit exceeded"
- Free tier: 60 requests/minute
- Solution: Add delays or upgrade to paid tier
- Or use `--dry-run` for testing

### "Model not found"
- Check model name spelling (case-sensitive)
- Ensure `:free` suffix for free models
- Visit https://openrouter.ai/models for full list

## 🎓 Learn More

- OpenRouter Models: https://openrouter.ai/models
- Free Models List: https://openrouter.ai/models?free=true
- API Documentation: https://openrouter.ai/docs
