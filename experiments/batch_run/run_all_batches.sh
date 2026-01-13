#!/bin/bash
# Run all 5 batches sequentially with user prompts
# Usage: ./run_all_batches.sh

set -e

TOTAL_BATCHES=5

echo "========================================"
echo "TaxMate Benchmark - All Batches"
echo "========================================"
echo ""
echo "This will run ${TOTAL_BATCHES} batches of 100 profiles each"
echo "Estimated time: 25-30 minutes"
echo "Estimated cost: \$7.50 - \$10.00"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

for i in $(seq 1 $TOTAL_BATCHES); do
    echo ""
    echo "========================================"
    echo "Starting Batch $i of $TOTAL_BATCHES"
    echo "========================================"
    
    ./run_batch.sh $i
    
    if [ $? -ne 0 ]; then
        echo "❌ Batch $i failed. Stopping."
        exit 1
    fi
    
    # Ask to continue (except after last batch)
    if [ $i -lt $TOTAL_BATCHES ]; then
        echo ""
        read -p "Batch $i complete. Continue to Batch $(($i+1))? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Stopped after Batch $i"
            echo "You can resume later by running: ./run_batch.sh $(($i+1))"
            exit 0
        fi
    fi
done

echo ""
echo "========================================"
echo "🎉 All Batches Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Merge results: python3 merge_results.py"
echo "2. Analyze data: python3 analyze_results.py"
echo "========================================"
