# Logging Setup Documentation

## Overview

Each of the four main files now has separate logging that writes to dedicated `.log` files in the `/logs` directory:

```
logs/
├── form_extraction.log      ← form_extraction.py logs
├── tax_comparison.log       ← tax_comparison.py logs
├── tax_advisor.log          ← tax_advisor.py logs
└── orchestrator.log         ← orchestrator.py logs
```

## Logging Configuration

Each file uses a rotating file handler that:
- **Max file size**: 5MB per log file
- **Backup count**: 2 (keeps 2 old backup files)
- **Encoding**: UTF-8
- **Format**: `YYYY-MM-DD HH:MM:SS - LEVEL - MESSAGE`
- **Location**: `/home/akash.prathap@acsiatech.com/taxmate/logs/`

## File-by-File Logging Details

### 1. **form_extraction.py**
**Logger**: `form_extraction`  
**Log File**: `form_extraction.log`

Logs:
- Form extraction process start
- Found PDF files and their paths
- Form loading results
- Any errors during extraction

Example log entries:
```
2025-12-08 15:30:45 - INFO - Starting form extraction process...
2025-12-08 15:30:46 - INFO - Found file: /path/to/Form_16_Part_B.pdf
2025-12-08 15:30:50 - INFO - Forms extraction complete. Found 3 deductions
```

### 2. **tax_comparison.py**
**Logger**: `tax_comparison`  
**Log File**: `tax_comparison.log`

Logs:
- Tax regime comparison start
- Input parameters (gross_salary, other_income, ch_via)
- JSON file loading
- Tax calculation results
- Optimal regime determination

Example log entries:
```
2025-12-08 15:31:00 - INFO - Starting tax regime comparison...
2025-12-08 15:31:00 - INFO - Input - gross_salary: 1500000, other_income: 100000, ch_via: 382402
2025-12-08 15:31:01 - INFO - Loading data from JSON files...
2025-12-08 15:31:02 - INFO - Optimal regime: NEW, Savings: ₹45000
```

### 3. **tax_advisor.py**
**Logger**: `tax_advisor`  
**Log File**: `tax_advisor.log`

Logs:
- Tax advice query start
- Question being asked
- Deductions provided (if any)
- Income details provided (if any)
- Advice generation success/failure
- Any errors encountered

Example log entries:
```
2025-12-08 15:31:10 - INFO - Getting tax advice for question: How can I pay less tax?
2025-12-08 15:31:10 - INFO - Deductions provided: 80C: ₹150000, 80D: ₹50000
2025-12-08 15:31:15 - INFO - Advice generated and logged successfully
```

### 4. **orchestrator.py**
**Logger**: `orchestrator`  
**Log File**: `orchestrator.log`

Logs:
- Orchestrator start with user question
- Intent analysis results
- Each workflow step completion
- Optimal regime determination
- Orchestrator completion

Example log entries:
```
2025-12-08 15:31:20 - INFO - ================================================================================
2025-12-08 15:31:20 - INFO - TAX FILING ORCHESTRATOR STARTED - Question: How can I pay less tax in the coming year?
2025-12-08 15:31:20 - INFO - ================================================================================
2025-12-08 15:31:21 - INFO - Analyzing intent: How can I pay less tax in the coming year?
2025-12-08 15:31:21 - INFO - Identified intents: extract_forms, compare_regimes, get_advice
2025-12-08 15:31:22 - INFO - Starting form extraction...
2025-12-08 15:31:25 - INFO - Starting tax regime comparison...
2025-12-08 15:31:26 - INFO - Tax comparison complete. Optimal regime: NEW
2025-12-08 15:31:27 - INFO - Starting tax advisor query...
2025-12-08 15:31:32 - INFO - Tax advice generated successfully
2025-12-08 15:31:33 - INFO - Summarizing orchestrator findings...
2025-12-08 15:31:33 - INFO - TAX FILING ORCHESTRATOR COMPLETED - Optimal regime: NEW
```

## How to View Logs

### View logs in real-time
```bash
# Watch orchestrator logs
tail -f logs/orchestrator.log

# Watch all logs
tail -f logs/*.log
```

### View recent entries
```bash
# Last 20 lines of form extraction
tail -20 logs/form_extraction.log

# Last 50 lines of tax comparison
tail -50 logs/tax_comparison.log
```

### Search logs
```bash
# Find all errors
grep ERROR logs/*.log

# Find all INFO messages for tax comparison
grep -i "INFO" logs/tax_comparison.log

# Find a specific question
grep "How can I pay less" logs/orchestrator.log
```

### Full log viewing
```bash
# View entire log file
cat logs/orchestrator.log

# View with less (paginated)
less logs/tax_advisor.log
```

## Log Rotation

Each log file automatically rotates when it exceeds 5MB:
- Original file: `orchestrator.log`
- First backup: `orchestrator.log.1`
- Second backup: `orchestrator.log.2`

Older backups are automatically removed.

## Integration with Orchestrator

The logging automatically happens when you run:

```bash
cd src/services
python3 orchestrator.py "How can I pay less tax in the coming year?"
```

All four log files will be updated simultaneously:
1. **orchestrator.log** - Top-level workflow
2. **form_extraction.log** - PDF extraction details
3. **tax_comparison.log** - Tax calculation details
4. **tax_advisor.log** - AI advice generation details

## Example: Complete Workflow Logging

When you run the orchestrator with a question, here's what gets logged:

**orchestrator.log**:
- Question and workflow start
- Intent analysis
- Step completion markers

**form_extraction.log**:
- Extraction start
- PDF file discoveries
- Extraction completion

**tax_comparison.log**:
- Comparison start
- Tax calculations
- Regime determination

**tax_advisor.log**:
- Question received
- Deductions processed
- Advice generation

## Troubleshooting

If logs aren't being created:
1. Check that `/logs` directory exists in project root
2. Verify file permissions on the logs directory
3. Check if the log files are being written to (use `ls -la logs/`)
4. Review console output for error messages

## Best Practices

1. **Regular log cleanup**: Archive old logs periodically
2. **Monitor errors**: Grep for ERROR level messages
3. **Track performance**: Look at timestamps to identify slow operations
4. **Debugging**: Use orchestrator.log as the entry point, then check individual tool logs

---

**Summary**: Each tool now maintains its own log file, making it easy to debug, audit, and understand the complete tax filing workflow.
