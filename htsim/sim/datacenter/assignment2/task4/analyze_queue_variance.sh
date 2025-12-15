#!/bin/bash

# Analyze Queue Length Variance for all load balancing algorithms

OUTPUT_DIR="$(pwd)/results"
IDMAP_FILE="${OUTPUT_DIR}/idmap.txt"
LB_ALGOS=("ecmp" "reps" "oblivious")

echo "============================================================="
echo "Queue Length Variance Analysis"
echo "============================================================="
echo ""

# Check if results exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Error: Results directory not found: $OUTPUT_DIR"
    echo "Please run run_congestion_experiments.sh first"
    exit 1
fi

# Check if idmap exists
if [ ! -f "$IDMAP_FILE" ]; then
    echo "Error: ID map file not found: $IDMAP_FILE"
    exit 1
fi

# Analyze each algorithm
for algo in "${LB_ALGOS[@]}"; do
    LOG_FILE="${OUTPUT_DIR}/logout_${algo}.dat"
    QUEUE_FILE="${OUTPUT_DIR}/queue_variance_${algo}.txt"
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "Warning: Log file not found: $LOG_FILE"
        echo "Skipping $algo"
        echo ""
        continue
    fi
    
    echo "-------------------------------------------------------------"
    echo "Analyzing: $algo"
    echo "-------------------------------------------------------------"
    
    python3 extract_queue_variance.py "$LOG_FILE" "$IDMAP_FILE" > "$QUEUE_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✓ Queue variance analysis completed: queue_variance_${algo}.txt"
        
        # Display summary
        echo ""
        echo "Summary for $algo:"
        grep -A 8 "Overall Queue Length Variance Statistics" "$QUEUE_FILE" | head -10
    else
        echo "✗ Queue variance analysis failed for $algo"
        echo "Check $QUEUE_FILE for details"
    fi
    
    echo ""
done

echo "============================================================="
echo "Queue Variance Analysis Complete"
echo "============================================================="
echo ""
echo "Detailed results saved in:"
for algo in "${LB_ALGOS[@]}"; do
    echo "  - results/queue_variance_${algo}.txt"
done
echo ""
