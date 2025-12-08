# Orchestrator Quick Reference

## What You Have Now

**1 new file**:
- `src/services/orchestrator.py` - Coordinates your 3 existing tools

**Uses your existing**:
- `form_extraction.py` 
- `tax_comparison.py`
- `tax_advisor.py`

## Run It

```bash
cd src/services
python3 orchestrator.py
```

Or with a question:
```bash
python3 orchestrator.py "What deductions can I claim?"
```

## What It Does

**Workflow**:
```
User Question
  ↓
Analyze Intent
  ↓
Extract Forms (calls form_extraction.py)
  ↓
Compare Regimes (uses tax_comparison.py logic)
  ↓
Get Advice (calls tax_advisor.py agent)
  ↓
Summarize & Log
  ↓
Final Report
```

## Key Features

✅ **Finds deductions** from extracted forms
✅ **Compares tax regimes** (old vs new)
✅ **Gets AI advice** from your existing agent
✅ **Logs everything** to `logs/orchestrator.log`
✅ **Your files unchanged** - No modifications to existing code

## Example Questions

```bash
python3 orchestrator.py "What deductions can I claim?"
python3 orchestrator.py "Can I claim both 80C and 80CCD(1B)?"
python3 orchestrator.py "Should I use old or new tax regime?"
python3 orchestrator.py "Extract my forms and provide advice"
```

## Output Example

```
================================================================================
TAX FILING ORCHESTRATOR SUMMARY
================================================================================

📄 EXTRACTED DATA:
  Forms found: 4

💰 DEDUCTIONS IDENTIFIED:
  • section_80C: ₹1,50,000
  • section_80D: ₹50,000
  • section_80CCD_1B: ₹50,000

📊 TAX REGIME COMPARISON:
  Gross Salary: ₹1,500,000
  Old Regime Tax: ₹150,000
  New Regime Tax: ₹120,000
  Optimal Regime: NEW
  Potential Savings: ₹30,000

🤖 TAX ADVICE:
Based on your income and deductions...
```

## How Deductions are Found

1. **Extract Forms** 
   - Calls `form_extraction.extract_all_forms()`
   - Loads JSON from `data/extracted/`

2. **Parse Deductions**
   - Looks in `Form_16_Part_B.deductions_chapter_VIA`
   - Extracts all non-zero values (80C, 80D, 80CCD, etc.)

3. **Use in Comparison**
   - Old regime: uses deductions to reduce taxable income
   - New regime: no deductions allowed

4. **Advise**
   - Passes deductions to your tax_advisor agent
   - Gets personalized recommendations

## Files

```
src/services/
├── orchestrator.py         ← NEW
├── form_extraction.py      ← YOUR EXISTING
├── tax_comparison.py       ← YOUR EXISTING
└── tax_advisor.py          ← YOUR EXISTING

logs/
└── orchestrator.log        ← AUTO-CREATED
```

## Python API

```python
from orchestrator import run_orchestrator

result = run_orchestrator("What's my optimal tax regime?")

# Access results:
print(result['deductions'])              # List of deductions
print(result['optimal_regime'])          # "NEW" or "OLD"
print(result['tax_comparison'])          # Tax calculations
print(result['tax_advice'])              # AI recommendations
```

## That's It!

**One command to get started**:
```bash
cd src/services && python3 orchestrator.py
```

Your 3 tools are now orchestrated together to:
- Extract tax forms
- Find deductions
- Compare tax regimes
- Provide AI advice
- Log everything

All without changing any of your existing code.
