#!/bin/bash

# Analyze Flow Completion Time (FCT) for all load balancing algorithms

OUTPUT_DIR="$(pwd)/results"
CONNECTION_MATRIX="congestion_scenario.cm"
LB_ALGOS=("ecmp" "reps" "oblivious")

echo "============================================================="
echo "Flow Completion Time (FCT) Analysis"
echo "============================================================="
echo ""

# Check if results exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Error: Results directory not found: $OUTPUT_DIR"
    echo "Please run run_congestion_experiments.sh first"
    exit 1
fi

# Analyze each algorithm
for algo in "${LB_ALGOS[@]}"; do
    OUTPUT_FILE="${OUTPUT_DIR}/congestion_${algo}.out"
    FCT_FILE="${OUTPUT_DIR}/fct_${algo}.txt"
    
    if [ ! -f "$OUTPUT_FILE" ]; then
        echo "Warning: Output file not found: $OUTPUT_FILE"
        echo "Skipping $algo"
        echo ""
        continue
    fi
    
    echo "-------------------------------------------------------------"
    echo "Analyzing: $algo"
    echo "-------------------------------------------------------------"
    
    python3 extract_fct.py "$OUTPUT_FILE" "$CONNECTION_MATRIX" > "$FCT_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✓ FCT analysis completed: fct_${algo}.txt"
        
        # Display summary
        echo ""
        echo "Summary for $algo:"
        grep -A 10 "Overall FCT Statistics" "$FCT_FILE" | head -15
    else
        echo "✗ FCT analysis failed for $algo"
        echo "Check $FCT_FILE for details"
    fi
    
    echo ""
done

echo "============================================================="
echo "FCT Analysis Complete"
echo "============================================================="
echo ""
echo "Detailed results saved in:"
for algo in "${LB_ALGOS[@]}"; do
    echo "  - results/fct_${algo}.txt"
done
echo ""
