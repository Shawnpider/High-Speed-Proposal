#!/bin/bash

# Task 4: Congestion Scenario Experiment with Multiple Senders and Receivers
# Tests different load balancing algorithms under realistic datacenter congestion
# Metrics: Flow Completion Time (FCT) and Queue Length Variance

# ===================================================================
# EXPERIMENT PARAMETERS
# ===================================================================
EXECUTABLE="../../htsim_uec"
TOPOLOGY="../../topologies/topo_assignment2/fat_tree_128_4os.topo"
CONNECTION_MATRIX="congestion_scenario.cm"

# Output Directory
OUTPUT_DIR="$(pwd)/results"
mkdir -p "$OUTPUT_DIR"

# Load Balancing Algorithms to test
LB_ALGOS=("ecmp" "reps" "oblivious")

# Simulation parameters
NODES=128
QUEUE_SIZE=100
ECN_LOW=20
ECN_HIGH=80
PATHS=200
CWND=1
MTU=1500
END_TIME=2000         # Extended time for multiple flows
LOG_TIME_US=100       # Queue sampling interval (microseconds)
SEED=42

# ===================================================================
# PRELIMINARY CHECKS
# ===================================================================
echo "============================================================="
echo "Task 4: Congestion Scenario Load Balancing Experiments"
echo "============================================================="
echo ""

# Check if executable exists
if [ ! -f "$EXECUTABLE" ]; then
    echo "Error: Executable not found: $EXECUTABLE"
    echo "Please compile the project first"
    echo ""
    echo "To compile:"
    echo "  cd ../../"
    echo "  mkdir -p build && cd build"
    echo "  cmake .. && make"
    exit 1
fi

# Check topology file
if [ ! -f "$TOPOLOGY" ]; then
    echo "Error: Topology file not found: $TOPOLOGY"
    exit 1
fi

# Check connection matrix file
if [ ! -f "$CONNECTION_MATRIX" ]; then
    echo "Error: Connection matrix file not found: $CONNECTION_MATRIX"
    exit 1
fi

# Display experiment configuration
echo "Experiment Configuration:"
echo "-------------------------"
echo "Topology: $TOPOLOGY"
echo "Connection Matrix: $CONNECTION_MATRIX"
echo "Output Directory: $OUTPUT_DIR"
echo "Load Balancing Algorithms: ${LB_ALGOS[@]}"
echo ""

# Display connection matrix info
echo "Traffic Pattern:"
echo "----------------"
TOTAL_FLOWS=$(grep "^Connections" "$CONNECTION_MATRIX" | awk '{print $2}')
echo "Total flows: $TOTAL_FLOWS"
echo ""
echo "Congestion Scenario Design:"
echo "  - Incast Pattern 1: 4 senders (0-3) -> receiver 16 (50MB each)"
echo "  - Incast Pattern 2: 4 senders (4-7) -> receiver 32 (50MB each)"
echo "  - Incast Pattern 3: 4 senders (8-11) -> receiver 48 (100MB each, delayed)"
echo "  - Incast Pattern 4: 4 senders (12-15) -> receiver 64 (100MB each, delayed)"
echo "  - Permutation Traffic: 8 flows (17-24) with various sizes (20MB)"
echo "  - Large Flows: 4 flows (33-36) with 150MB each"
echo "  - Medium Flows: 4 flows (49-52) with 80MB each"
echo ""
echo "This creates realistic datacenter congestion with:"
echo "  - Hotspot receivers (incast patterns)"
echo "  - Mixed flow sizes (20MB to 150MB)"
echo "  - Temporal overlap (staggered start times)"
echo ""
echo "============================================================="
echo ""

# ===================================================================
# RUN EXPERIMENTS FOR EACH LOAD BALANCING ALGORITHM
# ===================================================================
for algo in "${LB_ALGOS[@]}"; do
    echo ""
    echo "============================================================="
    echo "Running experiment: $algo"
    echo "============================================================="
    
    # Output files
    OUTPUT_FILE="${OUTPUT_DIR}/congestion_${algo}.out"
    
    # Run the simulation
    echo "Starting simulation..."
    echo "  Algorithm: $algo"
    echo "  Logging: Flow events and queue usage"
    echo ""
    
    $EXECUTABLE \
        -nodes $NODES \
        -topo "$TOPOLOGY" \
        -tm "$CONNECTION_MATRIX" \
        -sender_cc_algo dctcp \
        -load_balancing_algo "$algo" \
        -queue_type composite_ecn \
        -q $QUEUE_SIZE \
        -ecn $ECN_LOW $ECN_HIGH \
        -paths $PATHS \
        -cwnd $CWND \
        -mtu $MTU \
        -end $END_TIME \
        -log switch \
        -logtime_us $LOG_TIME_US \
        -seed $SEED \
        > "$OUTPUT_FILE" 2>&1
    
    # Check result
    if [ $? -eq 0 ]; then
        echo "✓ Simulation completed: $OUTPUT_FILE"
        
        # Move logout.dat to results directory with algorithm name
        if [ -f "logout.dat" ]; then
            mv logout.dat "${OUTPUT_DIR}/logout_${algo}.dat"
            echo "✓ Queue log saved: logout_${algo}.dat"
        fi
        
        # Move idmap.txt if it exists
        if [ -f "idmap.txt" ]; then
            if [ ! -f "${OUTPUT_DIR}/idmap.txt" ]; then
                cp idmap.txt "${OUTPUT_DIR}/idmap.txt"
            fi
        fi
        
    else
        echo "✗ Simulation failed: $OUTPUT_FILE"
        echo "   Check the output file for errors"
    fi
    
    echo ""
done

echo ""
echo "============================================================="
echo "All experiments completed!"
echo "============================================================="
echo ""
echo "Results saved in: $OUTPUT_DIR"
echo ""
echo "Next Steps:"
echo "-----------"
echo "1. Analyze Flow Completion Time (FCT):"
echo "   bash analyze_fct.sh"
echo ""
echo "2. Analyze Queue Length Variance:"
echo "   bash analyze_queue_variance.sh"
echo ""
echo "3. Generate comprehensive comparison:"
echo "   bash analyze_all.sh"
echo ""
echo "============================================================="
