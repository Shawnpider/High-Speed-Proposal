#!/bin/bash

# Comprehensive Analysis Script for Task 4
# Combines FCT and Queue Variance analysis with algorithm comparison

OUTPUT_DIR="$(pwd)/results"
SUMMARY_FILE="${OUTPUT_DIR}/comprehensive_analysis.txt"
LB_ALGOS=("ecmp" "reps" "oblivious")

echo "============================================================="
echo "Task 4: Comprehensive Performance Analysis"
echo "Congestion Scenario with Multiple Senders and Receivers"
echo "============================================================="
echo ""

# Check if results exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Error: Results directory not found: $OUTPUT_DIR"
    echo "Please run run_congestion_experiments.sh first"
    exit 1
fi

# Initialize summary file
cat > "$SUMMARY_FILE" << 'EOF'
=======================================================================
TASK 4: COMPREHENSIVE PERFORMANCE ANALYSIS
=======================================================================
Experiment: Congestion Scenario with Multiple Senders and Receivers
Date: $(date)

This analysis compares the performance of three load balancing algorithms
(ECMP, REPS, Oblivious) under realistic datacenter congestion conditions.

Traffic Pattern:
  - 32 total flows with mixed sizes (20MB to 150MB)
  - Multiple incast patterns (hotspot receivers)
  - Permutation traffic (distributed flows)
  - Temporal overlap (staggered start times)

Performance Metrics:
  1. Flow Completion Time (FCT)
  2. Queue Length Variance

=======================================================================

EOF

# Step 1: Analyze FCT for all algorithms
echo "Step 1: Analyzing Flow Completion Time (FCT)..."
echo ""

bash analyze_fct.sh

if [ $? -eq 0 ]; then
    echo "✓ FCT analysis completed"
else
    echo "⚠ FCT analysis had issues"
fi
echo ""

# Step 2: Analyze Queue Variance for all algorithms
echo "Step 2: Analyzing Queue Length Variance..."
echo ""

bash analyze_queue_variance.sh

if [ $? -eq 0 ]; then
    echo "✓ Queue variance analysis completed"
else
    echo "⚠ Queue variance analysis had issues"
fi
echo ""

# Step 3: Generate comparison summary
echo "Step 3: Generating comparison summary..."
echo ""

cat >> "$SUMMARY_FILE" << 'EOF'
=======================================================================
FLOW COMPLETION TIME (FCT) COMPARISON
=======================================================================

EOF

for algo in "${LB_ALGOS[@]}"; do
    FCT_FILE="${OUTPUT_DIR}/fct_${algo}.txt"
    
    if [ -f "$FCT_FILE" ]; then
        echo "--- ${algo^^} ---" >> "$SUMMARY_FILE"
        
        # Extract key statistics
        grep -A 12 "Overall FCT Statistics" "$FCT_FILE" >> "$SUMMARY_FILE" 2>/dev/null
        
        # Extract incast analysis
        echo "" >> "$SUMMARY_FILE"
        grep -A 20 "Incast Pattern Analysis" "$FCT_FILE" >> "$SUMMARY_FILE" 2>/dev/null
        
        echo "" >> "$SUMMARY_FILE"
        echo "-----------------------------------------------------------------------" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
    fi
done

cat >> "$SUMMARY_FILE" << 'EOF'

=======================================================================
QUEUE LENGTH VARIANCE COMPARISON
=======================================================================

EOF

for algo in "${LB_ALGOS[@]}"; do
    QUEUE_FILE="${OUTPUT_DIR}/queue_variance_${algo}.txt"
    
    if [ -f "$QUEUE_FILE" ]; then
        echo "--- ${algo^^} ---" >> "$SUMMARY_FILE"
        
        # Extract overall statistics
        grep -A 10 "Overall Queue Length Variance Statistics" "$QUEUE_FILE" >> "$SUMMARY_FILE" 2>/dev/null
        
        echo "" >> "$SUMMARY_FILE"
        echo "-----------------------------------------------------------------------" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
    fi
done

# Step 4: Generate comparative summary table
cat >> "$SUMMARY_FILE" << 'EOF'

=======================================================================
COMPARATIVE SUMMARY TABLE
=======================================================================

EOF

# Extract key metrics for comparison
echo "Algorithm          Mean FCT (ms)    P95 FCT (ms)    Spatial Var.     Max Queue" >> "$SUMMARY_FILE"
echo "----------------   --------------   -------------   -------------   -----------" >> "$SUMMARY_FILE"

for algo in "${LB_ALGOS[@]}"; do
    FCT_FILE="${OUTPUT_DIR}/fct_${algo}.txt"
    QUEUE_FILE="${OUTPUT_DIR}/queue_variance_${algo}.txt"
    
    # Extract metrics
    # Pattern: "Mean FCT: 38545.97 us (38.55 ms)"
    mean_fct=$(grep "Mean FCT:" "$FCT_FILE" 2>/dev/null | grep -o '([0-9.]*' | sed 's/(//' | head -1)
    p95_fct=$(grep "P95:" "$FCT_FILE" 2>/dev/null | grep -o '([0-9.]*' | sed 's/(//' | head -1)
    # NEW: Extract spatial variance (variance among switches)
    spatial_var=$(grep "Variance Among Switches:" "$QUEUE_FILE" 2>/dev/null | awk '{print $4}')
    max_queue=$(grep "Peak Queue Observed:" "$QUEUE_FILE" 2>/dev/null | awk '{print $4}')
    
    # Format output
    printf "%-18s %-16s %-15s %-15s %-12s\n" \
        "${algo}" \
        "${mean_fct:-N/A}" \
        "${p95_fct:-N/A}" \
        "${spatial_var:-N/A}" \
        "${max_queue:-N/A}" >> "$SUMMARY_FILE"
done

cat >> "$SUMMARY_FILE" << 'EOF'

=======================================================================
ANALYSIS INTERPRETATION GUIDE
=======================================================================

Flow Completion Time (FCT):
  - Lower Mean FCT: Better average performance
  - Lower P95 FCT: More consistent performance, fewer stragglers
  - Lower variance in FCT: More predictable flow completion

Spatial Variance (Load Balancing Metric):
  - Variance AMONG switches (not over time)
  - Lower Spatial Variance: More evenly distributed load across switches
  - Lower Max Queue: Better congestion management
  - Measures how balanced the load is across the network

Expected Algorithm Characteristics:
  - ECMP: Simple hash-based routing, may create hotspots
  - REPS: Adaptive routing, should balance load better across switches
  - Oblivious: Random path selection, theoretical load balance

=======================================================================
RESULTS INTERPRETATION
=======================================================================

Based on your results above, analyze:

1. Which algorithm achieved the lowest mean and P95 FCT?
   → This indicates the best overall and tail performance

2. Which algorithm had the lowest spatial variance?
   → This indicates the best load balancing (most evenly distributed)

3. Are there trade-offs between FCT and spatial variance?
   → Some algorithms may achieve fast FCT by concentrating traffic

4. How do incast patterns affect each algorithm?
   → Compare FCT variance within incast groups across algorithms

5. Does the congestion scenario reveal algorithm weaknesses?
   → Look for algorithms that struggle with specific traffic patterns

=======================================================================
DETAILED RESULTS
=======================================================================

For detailed per-flow and per-switch results, see:
  - results/fct_<algorithm>.txt (Flow-level FCT statistics)
  - results/queue_variance_<algorithm>.txt (Switch-level queue statistics)

=======================================================================

EOF

echo "✓ Comparison summary generated"
echo ""

# Display summary
echo "============================================================="
echo "COMPREHENSIVE ANALYSIS SUMMARY"
echo "============================================================="
echo ""

cat "$SUMMARY_FILE"

echo ""
echo "============================================================="
echo "Analysis Complete"
echo "============================================================="
echo ""
echo "Full report saved to: $SUMMARY_FILE"
echo ""
echo "Individual analysis files:"
for algo in "${LB_ALGOS[@]}"; do
    echo "  - results/fct_${algo}.txt"
    echo "  - results/queue_variance_${algo}.txt"
done
echo ""
echo "To view the full report:"
echo "  cat $SUMMARY_FILE"
echo ""
