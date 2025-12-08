# Logging Directory Structure

## Complete Log File Organization

```
/home/akash.prathap@acsiatech.com/taxmate/
├── logs/
│   ├── form_extraction.log      ← Logs from form_extraction.py
│   ├── form_extraction.log.1    ← Backup (auto-rotated when >5MB)
│   ├── form_extraction.log.2    ← Older backup
│   │
│   ├── tax_comparison.log       ← Logs from tax_comparison.py
│   ├── tax_comparison.log.1     ← Backup
│   ├── tax_comparison.log.2     ← Older backup
│   │
│   ├── tax_advisor.log          ← Logs from tax_advisor.py
│   ├── tax_advisor.log.1        ← Backup
│   ├── tax_advisor.log.2        ← Older backup
│   │
│   ├── orchestrator.log         ← Logs from orchestrator.py
│   ├── orchestrator.log.1       ← Backup
│   └── orchestrator.log.2       ← Older backup
│
└── src/
    ├── services/
    │   ├── orchestrator.py          ← Uses all 3 tools + logs
    │   ├── form_extraction.py       ← Logs to form_extraction.log
    │   ├── tax_comparison.py        ← Logs to tax_comparison.log
    │   └── tax_advisor.py           ← Logs to tax_advisor.log
    │
    └── utils/
        └── logger.py                ← Original logger utility (still available)
```

## Log File Sizes

Each log file:
- **Initial size**: 0 KB (created on first run)
- **Max size before rotation**: 5 MB
- **Number of backups kept**: 2
- **Auto-cleanup**: Oldest backup deleted when new one created

Example rotation:
1. `orchestrator.log` reaches 5MB
2. Automatically renamed to `orchestrator.log.1`
3. New empty `orchestrator.log` created
4. If `orchestrator.log.1` exists and new one is created → renamed to `orchestrator.log.2`
5. Old `orchestrator.log.2` is deleted

## Log File Contents

### form_extraction.log
```
2025-12-08 15:30:45 - INFO - Starting form extraction process...
2025-12-08 15:30:46 - INFO - Found file: /path/to/Form_16_Part_B.pdf
2025-12-08 15:30:50 - INFO - Forms extraction complete. Found 3 deductions
```

### tax_comparison.log
```
2025-12-08 15:31:00 - INFO - Starting tax regime comparison...
2025-12-08 15:31:00 - INFO - Input - gross_salary: 1500000, other_income: 100000, ch_via: 382402
2025-12-08 15:31:01 - INFO - Loading data from JSON files...
```

### tax_advisor.log
```
2025-12-08 15:31:10 - INFO - Getting tax advice for question: How can I pay less tax?
2025-12-08 15:31:10 - INFO - Deductions provided: 80C: ₹150000, 80D: ₹50000
2025-12-08 15:31:15 - INFO - Advice generated and logged successfully
```

### orchestrator.log
```
2025-12-08 15:31:20 - INFO - ================================================================================
2025-12-08 15:31:20 - INFO - TAX FILING ORCHESTRATOR STARTED - Question: How can I pay less tax?
2025-12-08 15:31:21 - INFO - Analyzing intent: How can I pay less tax in the coming year?
2025-12-08 15:31:21 - INFO - Identified intents: extract_forms, compare_regimes, get_advice
2025-12-08 15:31:25 - INFO - TAX FILING ORCHESTRATOR COMPLETED - Optimal regime: NEW
```

## Accessing Logs

### View directory contents
```bash
cd /home/akash.prathap@acsiatech.com/taxmate
ls -lah logs/
```

### Monitor in real-time
```bash
# Watch orchestrator logs
tail -f logs/orchestrator.log

# Watch all logs in parallel
tail -f logs/*.log

# Watch specific tool logs
tail -f logs/tax_comparison.log
```

### Search logs
```bash
# Find errors across all logs
grep -r "ERROR" logs/

# Find specific text
grep "Optimal regime" logs/orchestrator.log

# Count log entries by level
grep -c "INFO" logs/tax_comparison.log
```

### Archive old logs
```bash
# Create backup of logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/

# Clear all logs but keep them
for f in logs/*.log*; do > "$f"; done
```

## Logger Configuration Summary

| Logger Name | Log File | Max Size | Backups | Level | Format |
|-------------|----------|----------|---------|-------|--------|
| form_extraction | form_extraction.log | 5 MB | 2 | INFO | ISO timestamp + level + message |
| tax_comparison | tax_comparison.log | 5 MB | 2 | INFO | ISO timestamp + level + message |
| tax_advisor | tax_advisor.log | 5 MB | 2 | INFO | ISO timestamp + level + message |
| orchestrator | orchestrator.log | 5 MB | 2 | INFO | ISO timestamp + level + message |

## Console Output

All loggers also output to **console** for real-time feedback:
```
INFO: Analyzing intent: How can I pay less tax?
INFO: Tax comparison complete. Optimal regime: NEW
INFO: Tax advice generated successfully
```

## Troubleshooting Logs

### Logs not being created?
```bash
# Check if logs directory exists and is writable
ls -ld /home/akash.prathap@acsiatech.com/taxmate/logs/

# Create if missing
mkdir -p /home/akash.prathap@acsiatech.com/taxmate/logs/

# Check permissions
chmod 755 /home/akash.prathap@acsiatech.com/taxmate/logs/
```

### Clear logs
```bash
# Clear all logs
rm -f /home/akash.prathap@acsiatech.com/taxmate/logs/*.log*

# Or individual logs
rm -f /home/akash.prathap@acsiatech.com/taxmate/logs/orchestrator.log*
```

### Check for errors
```bash
# Find all errors
grep "ERROR" /home/akash.prathap@acsiatech.com/taxmate/logs/*.log

# Find warnings
grep "WARNING" /home/akash.prathap@acsiatech.com/taxmate/logs/*.log
```

---

**Logging is fully configured in separate files for each tool!** 🎯
