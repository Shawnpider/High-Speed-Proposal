#!/bin/bash

# Quick Start Guide for Task 4
# This script will guide you through running the experiment

echo "=================================================================="
echo "TASK 4: QUICK START GUIDE"
echo "Congestion Scenario Load Balancing Experiment"
echo "=================================================================="
echo ""
echo "This experiment will:"
echo "  1. Run simulations with ECMP, REPS, and Oblivious routing"
echo "  2. Analyze Flow Completion Time (FCT)"
echo "  3. Analyze Queue Length Variance"
echo "  4. Generate comprehensive comparison"
echo ""
echo "Estimated time: 20-40 minutes"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check if executable exists
if [ ! -f "../../htsim_uec" ]; then
    echo "❌ Error: htsim_uec executable not found"
    echo ""
    echo "Please compile the project first:"
    echo "  cd ../../"
    echo "  mkdir -p build && cd build"
    echo "  cmake .."
    echo "  make"
    echo ""
    exit 1
else
    echo "✓ htsim_uec executable found"
fi

# Check topology
if [ ! -f "../../topologies/topo_assignment2/fat_tree_128_4os.topo" ]; then
    echo "❌ Error: Topology file not found"
    exit 1
else
    echo "✓ Topology file found"
fi

# Check connection matrix
if [ ! -f "congestion_scenario.cm" ]; then
    echo "❌ Error: Connection matrix not found"
    exit 1
else
    echo "✓ Connection matrix found"
fi

# Check parse_output
PARSE_OUTPUT=""
if [ -f "../../../../build/parse_output" ]; then
    PARSE_OUTPUT="../../../../build/parse_output"
elif [ -f "../../../build/parse_output" ]; then
    PARSE_OUTPUT="../../../build/parse_output"
fi

if [ -z "$PARSE_OUTPUT" ]; then
    echo "⚠  Warning: parse_output not found (needed for queue analysis)"
    echo "   To compile: cd ../../build && make parse_output"
    echo ""
else
    echo "✓ parse_output found"
fi

echo ""
echo "Prerequisites check complete!"
echo ""

# Ask user if they want to continue
echo "Do you want to start the experiment? (y/n)"
read -r response

if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Experiment cancelled."
    exit 0
fi

echo ""
echo "=================================================================="
echo "STARTING EXPERIMENT"
echo "=================================================================="
echo ""

# Step 1: Run experiments
echo "STEP 1/4: Running simulations for all algorithms..."
echo "This will take approximately 20-30 minutes..."
echo ""

bash run_congestion_experiments.sh

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Experiment failed. Check output above for errors."
    exit 1
fi

echo ""
echo "✓ Simulations completed!"
echo ""

# Step 2: Analyze results
echo "=================================================================="
echo "STEP 2/4: Running comprehensive analysis..."
echo "=================================================================="
echo ""

bash analyze_all.sh

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠  Analysis had some issues, but results may still be available."
fi

echo ""
echo "=================================================================="
echo "EXPERIMENT COMPLETE!"
echo "=================================================================="
echo ""
echo "Results are available in the 'results/' directory:"
echo ""
echo "📊 Main Report:"
echo "   results/comprehensive_analysis.txt"
echo ""
echo "📈 Detailed Results:"
echo "   - FCT Analysis: results/fct_<algorithm>.txt"
echo "   - Queue Analysis: results/queue_variance_<algorithm>.txt"
echo ""
echo "📁 Raw Data:"
echo "   - Simulation output: results/congestion_<algorithm>.out"
echo "   - Queue logs: results/logout_<algorithm>.dat"
echo ""
echo "To view the main report:"
echo "   cat results/comprehensive_analysis.txt"
echo ""
echo "To view individual results:"
echo "   cat results/fct_ecmp.txt"
echo "   cat results/queue_variance_ecmp.txt"
echo ""
echo "=================================================================="
