# Logging Examples & Reference

## Complete Logging Output Example

When you run this command:
```bash
python3 orchestrator.py "How can I pay less tax in the coming year?"
```

Here's what gets logged to each file:

---

## 1. orchestrator.log

```
================================================================================
2025-12-08 15:31:20 - INFO - TAX FILING ORCHESTRATOR STARTED - Question: How can I pay less tax in the coming year?
================================================================================
2025-12-08 15:31:21 - INFO - Analyzing intent: How can I pay less tax in the coming year?
2025-12-08 15:31:21 - INFO - Identified intents: extract_forms, compare_regimes, get_advice
2025-12-08 15:31:22 - INFO - Starting form extraction...
2025-12-08 15:31:23 - INFO - Starting tax regime comparison...
2025-12-08 15:31:23 - INFO - Tax comparison complete. Optimal regime: NEW
2025-12-08 15:31:24 - INFO - Starting tax advisor query...
2025-12-08 15:31:30 - INFO - Tax advice generated successfully
2025-12-08 15:31:31 - INFO - Summarizing orchestrator findings...
2025-12-08 15:31:31 - INFO - TAX FILING ORCHESTRATOR COMPLETED - Optimal regime: NEW
================================================================================
```

---

## 2. form_extraction.log

```
2025-12-08 15:31:22 - INFO - Starting form extraction process...
2025-12-08 15:31:22 - INFO - Found file: /home/akash.prathap@acsiatech.com/taxmate/data/extracted/Form_16_Part_A_20251208_152605.json
2025-12-08 15:31:22 - INFO - Found file in search directories: /home/akash.prathap@acsiatech.com/taxmate/data/extracted/Form_16_Part_A_20251208_152605.json
2025-12-08 15:31:22 - INFO - Found file: /home/akash.prathap@acsiatech.com/taxmate/data/extracted/Form_16_Part_B_20251208_152605.json
2025-12-08 15:31:22 - INFO - Loaded Form_16_Part_A_20251208_152605
2025-12-08 15:31:22 - INFO - Loaded Form_16_Part_B_20251208_152605
2025-12-08 15:31:23 - INFO - Forms extraction complete. Found 3 deductions
```

---

## 3. tax_comparison.log

```
2025-12-08 15:31:23 - INFO - Starting tax regime comparison...
2025-12-08 15:31:23 - INFO - Input - gross_salary: 1500000, other_income: 100000, ch_via: 382402
2025-12-08 15:31:23 - INFO - Tax regime comparison complete:
  Old Regime Taxable Income: ₹1,117,598
  Old Regime Tax: ₹143,519
  New Regime Taxable Income: ₹1,500,000
  New Regime Tax: ₹98,519
  Optimal Regime: NEW
  Tax Savings: ₹45,000
```

---

## 4. tax_advisor.log

```
2025-12-08 15:31:24 - INFO - Getting tax advice for question: How can I pay less tax in the coming year?
2025-12-08 15:31:24 - INFO - Deductions provided: section_80C: ₹150000, section_80D: ₹50000, section_80CCD_1B: ₹50000
2025-12-08 15:31:24 - INFO - Income details provided: Gross Salary: ₹1,500,000, Other Income: ₹100,000, Optimal Regime: NEW
2025-12-08 15:31:24 - INFO - Tax advisor invoked with question: How can I pay less tax in the coming year?
2025-12-08 15:31:30 - INFO - Advice generated and logged successfully
```

---

## Console Output (Simultaneous)

While logs are being written, you also see this on the console:

```
================================================================================
🎯 TAX FILING ORCHESTRATOR STARTED
================================================================================
Question: How can I pay less tax in the coming year?

🔍 Analyzing intent: How can I pay less tax in the coming year?
✓ Identified intents: extract_forms, compare_regimes, get_advice

📄 Extracting forms using form_extraction.py...
✓ Loaded Form_16_Part_A_20251208_152605
✓ Loaded Form_16_Part_B_20251208_152605
✓ Forms extraction complete. Found 3 deductions

📊 Comparing tax regimes using tax_comparison.py...
======================================================================
OLD REGIME TAX CALCULATION (with deductions like 80C, 80D, etc.)
======================================================================
  Gross Salary (present + other)      : ₹ 1,600,000
  Less: Standard deduction (u/s 16)   : ₹ 50,000
  Salary after standard deduction     : ₹ 1,550,000
  Other income                        : ₹ 100,000
  Gross total income                  : ₹ 1,650,000
  Less: Deductions (80C, 80D, etc.)   : ₹ 382,402
  Taxable income (old)                : ₹ 1,267,598
  TAX LIABILITY (before cess)         : ₹ 143,519 ✓

======================================================================
NEW REGIME TAX CALCULATION (Simplified - No deductions allowed)
======================================================================
  Gross Salary (present + other)      : ₹ 1,600,000
  Less: Standard deduction (u/s 16)   : ₹ 50,000
  Salary after standard deduction     : ₹ 1,550,000
  Other income                        : ₹ 100,000
  Gross total income                  : ₹ 1,650,000
  Less: Deductions (No deductions)    : ₹ 0
  Taxable income (new)                : ₹ 1,650,000
  TAX LIABILITY (before cess)         : ₹ 187,500 ✓

🎯 OPTIMAL REGIME: NEW REGIME
💡 Tax Savings: ₹ 45,000

🤖 Getting tax advice using tax_advisor.py...
✓ Tax advice generated

================================================================================
TAX FILING ORCHESTRATOR SUMMARY
================================================================================

📄 EXTRACTED DATA:
  Forms found: 2

💰 DEDUCTIONS IDENTIFIED:
  • section_80C: ₹150,000
  • section_80D: ₹50,000
  • section_80CCD_1B: ₹50,000

[Detailed tax calculation and analysis displayed]

🤖 AI TAX ADVISOR RECOMMENDATIONS:
As a tax accountant, based on your income and deductions...
[AI-generated recommendations]

================================================================================
✅ ORCHESTRATOR COMPLETED
================================================================================
```

---

## Searching and Filtering Logs

### Find all deductions
```bash
grep "Deductions provided" logs/tax_advisor.log
```
Output:
```
2025-12-08 15:31:24 - INFO - Deductions provided: section_80C: ₹150000, section_80D: ₹50000
```

### Find optimal regime decisions
```bash
grep "Optimal regime" logs/tax_comparison.log
```
Output:
```
2025-12-08 15:31:23 - INFO - Optimal Regime: NEW
2025-12-08 15:32:15 - INFO - Optimal Regime: OLD
2025-12-08 15:33:02 - INFO - Optimal Regime: EQUAL
```

### Find errors
```bash
grep "ERROR" logs/*.log
```

### Timeline of execution
```bash
grep "2025-12-08 15:31" logs/orchestrator.log | head -20
```

### Count entries per file
```bash
wc -l logs/*.log
```
Output:
```
   15 logs/form_extraction.log
   10 logs/tax_comparison.log
    8 logs/tax_advisor.log
   25 logs/orchestrator.log
   58 total
```

---

## Log Rotation Example

### Day 1 (Fresh Start)
```
logs/
├── form_extraction.log      (size: 1.2 KB)
├── tax_comparison.log       (size: 0.8 KB)
├── tax_advisor.log          (size: 1.5 KB)
└── orchestrator.log         (size: 2.1 KB)
```

### Day 10 (After many runs)
```
logs/
├── form_extraction.log      (size: 5.0 MB)
├── form_extraction.log.1    (size: 5.0 MB)
├── tax_comparison.log       (size: 3.2 MB)
├── tax_comparison.log.1     (size: 5.0 MB)
├── tax_advisor.log          (size: 4.1 MB)
├── tax_advisor.log.1        (size: 5.0 MB)
├── orchestrator.log         (size: 4.8 MB)
└── orchestrator.log.1       (size: 5.0 MB)
```

When a file exceeds 5 MB:
1. Current file renamed to `.log.1`
2. Previous `.log.1` renamed to `.log.2` (if exists)
3. Previous `.log.2` deleted
4. New empty `.log` file created

---

## Real-Time Monitoring

### Watch orchestrator execution
```bash
tail -f logs/orchestrator.log
```

### Watch all logs simultaneously
```bash
tail -f logs/*.log
```

### Follow with timestamps
```bash
tail -f logs/tax_advisor.log | while IFS= read -r line; do echo "[$(date '+%H:%M:%S')] $line"; done
```

### Monitor file sizes
```bash
watch -n 5 'ls -lh logs/'
```
Updates every 5 seconds

---

## Advanced Log Analysis

### Extract unique deductions
```bash
grep "Deductions provided" logs/tax_advisor.log | cut -d: -f2- | sort -u
```

### Count how many times "NEW" regime was optimal
```bash
grep "Optimal Regime: NEW" logs/tax_comparison.log | wc -l
```

### Get average tax savings
```bash
grep "Tax Savings:" logs/tax_comparison.log | \
  grep -oE '₹ [0-9,]+' | \
  tr -d '₹, ' | \
  awk '{sum+=$1; count++} END {print "Average: ₹" int(sum/count)}'
```

### Execution time analysis
```bash
# Get start and end times
echo "Start: $(head -1 logs/orchestrator.log | cut -d' ' -f1-2)"
echo "End: $(tail -1 logs/orchestrator.log | cut -d' ' -f1-2)"
```

---

## Tips & Best Practices

1. **Daily Backups**: Archive logs at end of day
   ```bash
   tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/*.log
   ```

2. **Monitor Growth**: Check log sizes weekly
   ```bash
   du -sh logs/
   ```

3. **Clean Up**: Remove old backups after archiving
   ```bash
   find logs/ -name "*.log.2" -delete
   ```

4. **Search Efficiently**: Use grep with context
   ```bash
   grep -B2 -A2 "ERROR" logs/*.log
   ```

5. **Automate Monitoring**: Set up cron job
   ```bash
   # Run analysis daily at 23:00
   0 23 * * * grep "ERROR" /path/to/logs/*.log | mail -s "Daily Log Report" admin@example.com
   ```

---

**Happy logging!** 📊🎯
