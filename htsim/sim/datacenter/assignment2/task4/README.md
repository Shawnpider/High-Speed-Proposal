# Task 4: Congestion Scenario Analysis with Multiple Senders and Receivers

## Overview

Task 4 implements a realistic datacenter congestion scenario to evaluate the performance of different load balancing algorithms (ECMP, REPS, Oblivious) under stress conditions with multiple concurrent flows.

## Objectives

1. **Design a Congestion Scenario**: Create realistic datacenter traffic patterns that cause network congestion
2. **Evaluate Load Balancing Algorithms**: Compare ECMP, REPS, and Oblivious routing under congestion
3. **Measure Performance Metrics**:
   - Flow Completion Time (FCT) - How quickly flows complete
   - Queue Length Variance - How balanced the load is across switches

## Experiment Design

### Congestion Scenario (`congestion_scenario.cm`)

The experiment uses **32 concurrent flows** with the following patterns:

#### 1. Incast Patterns (Hotspot Receivers)
Creates congestion at specific receivers by having multiple senders target the same destination:

- **Incast Group 1**: 4 senders (0-3) → receiver 16 (50MB each, start at 0μs)
- **Incast Group 2**: 4 senders (4-7) → receiver 32 (50MB each, start at 0μs)
- **Incast Group 3**: 4 senders (8-11) → receiver 48 (100MB each, start at 100μs)
- **Incast Group 4**: 4 senders (12-15) → receiver 64 (100MB each, start at 100μs)

#### 2. Permutation Traffic (Distributed Flows)
Creates general network congestion with one-to-one flows:

- **8 flows** (17-24) with 20MB each, starting at 200μs
- Distributed across different sender-receiver pairs

#### 3. Large Flows (Bandwidth Intensive)
Long-running flows that compete with other traffic:

- **4 flows** (33-36) with 150MB each, starting at 300μs

#### 4. Medium Flows (Mixed Workload)
Additional medium-sized flows for realistic workload:

- **4 flows** (49-52) with 80MB each, starting at 400μs

### Why This Design?

This congestion scenario mimics real datacenter patterns:

1. **Incast Patterns**: Common in distributed systems (MapReduce reduce phase, distributed storage reads)
2. **Mixed Flow Sizes**: Realistic datacenter traffic has heterogeneous flow sizes
3. **Temporal Overlap**: Staggered start times create dynamic congestion
4. **Hotspots**: Multiple flows converging on same receiver stress the load balancing

## Topology

- **Fat-tree topology**: 128 nodes, 3-tier (ToR, Aggregation, Core), 4x oversubscribed
- **File**: `fat_tree_128_4os.topo`
- **Core switches**: Where we measure queue variance
- **Multiple paths**: Different load balancing algorithms can choose different routes

## Performance Metrics

### 1. Flow Completion Time (FCT)

**Definition**: Time from flow start to completion

**Why Important**:
- Direct measure of user-perceived performance
- Lower FCT = faster data transfer
- Tail FCT (P95, P99) indicates consistency

**What We Measure**:
- Mean FCT across all flows
- Median FCT (50th percentile)
- Tail latency (P95, P99)
- Per-flow FCT
- FCT by flow size category
- FCT variance within incast groups

### 2. Queue Length Variance

**Definition**: Variation in queue occupancy across core switches over time

**Why Important**:
- Indicates load balancing effectiveness
- Lower variance = more balanced load distribution
- High variance = some switches overloaded, others underutilized
- Affects overall network utilization

**What We Measure**:
- Per-switch queue statistics (mean, max, variance)
- Overall mean variance across all core switches
- Maximum queue lengths observed

## Files and Scripts

### Configuration Files
- **`congestion_scenario.cm`**: Connection matrix defining all flows
- Uses topology: `../../topologies/topo_assignment2/fat_tree_128_4os.topo`

### Execution Scripts
- **`run_congestion_experiments.sh`**: Main script to run experiments for all algorithms
- **`analyze_fct.sh`**: Analyze Flow Completion Time for all algorithms
- **`analyze_queue_variance.sh`**: Analyze queue variance for all algorithms
- **`analyze_all.sh`**: Comprehensive analysis combining both metrics

### Analysis Scripts (Python)
- **`extract_fct.py`**: Extract FCT from simulation output
- **`extract_queue_variance.py`**: Extract queue statistics from binary logs

### Output Directory Structure
```
results/
├── congestion_ecmp.out           # Simulation output (ECMP)
├── congestion_reps.out           # Simulation output (REPS)
├── congestion_oblivious.out      # Simulation output (Oblivious)
├── logout_ecmp.dat               # Binary queue log (ECMP)
├── logout_reps.dat               # Binary queue log (REPS)
├── logout_oblivious.dat          # Binary queue log (Oblivious)
├── idmap.txt                     # Switch ID mapping
├── fct_ecmp.txt                  # FCT analysis (ECMP)
├── fct_reps.txt                  # FCT analysis (REPS)
├── fct_oblivious.txt             # FCT analysis (Oblivious)
├── queue_variance_ecmp.txt       # Queue analysis (ECMP)
├── queue_variance_reps.txt       # Queue analysis (REPS)
├── queue_variance_oblivious.txt  # Queue analysis (Oblivious)
└── comprehensive_analysis.txt    # Combined comparison
```

## Usage

### Prerequisites

1. **Compile the simulator**:
```bash
cd ../../  # Go to htsim/sim/datacenter
mkdir -p build && cd build
cmake ..
make
```

2. **Verify topology and connection matrix exist**:
```bash
ls ../../topologies/topo_assignment2/fat_tree_128_4os.topo
ls congestion_scenario.cm
```

### Running the Experiments

#### Step 1: Run All Experiments
```bash
bash run_congestion_experiments.sh
```

This will:
- Run simulations for ECMP, REPS, and Oblivious
- Each simulation takes approximately 5-10 minutes
- Generate output and log files for each algorithm
- Total time: ~15-30 minutes

#### Step 2: Analyze Results

**Option A: Run Individual Analyses**
```bash
# Analyze FCT
bash analyze_fct.sh

# Analyze queue variance
bash analyze_queue_variance.sh
```

**Option B: Run Comprehensive Analysis (Recommended)**
```bash
bash analyze_all.sh
```

This generates a complete comparison report in `results/comprehensive_analysis.txt`

### Making Scripts Executable

If you get permission errors, make scripts executable:
```bash
chmod +x *.sh
```

## Understanding the Results

### Flow Completion Time Analysis

**Key Metrics to Compare**:
- **Mean FCT**: Lower is better (average performance)
- **P95/P99 FCT**: Lower is better (tail latency, fewer stragglers)
- **FCT by category**: Compare small, medium, large flows
- **Incast FCT**: Higher variance indicates poor handling of hotspots

**Example Interpretation**:
```
Algorithm: REPS
Mean FCT: 1250.50 ms
P95 FCT: 2100.30 ms
```
This shows REPS completes flows in 1.25s on average, with 95% completing within 2.1s.

### Queue Variance Analysis

**Key Metrics to Compare**:
- **Mean Variance**: Lower is better (more balanced load)
- **Max Queue Length**: Lower is better (less congestion)
- **Variance across switches**: Uniformity indicates good load balancing

**Example Interpretation**:
```
Algorithm: ECMP
Mean Variance: 15234.56 bytes²
Max Queue Length: 850000 bytes
```
Higher variance suggests uneven load distribution across core switches.

### Comparative Analysis

The comprehensive analysis (`analyze_all.sh`) produces a comparison table:

```
Algorithm          Mean FCT (ms)    P95 FCT (ms)    Mean Variance    Max Queue
----------------   --------------   -------------   -------------   -----------
ecmp               1250.50          2100.30         15234.56        850000
reps               1180.20          1950.10         12456.78        780000
oblivious          1310.80          2200.50         11234.90        820000
```

**How to Interpret**:
1. **Best FCT**: Which algorithm has lowest mean and P95?
2. **Best Load Balancing**: Which has lowest queue variance?
3. **Trade-offs**: Does one algorithm excel in one metric but lag in another?

## Expected Algorithm Behavior

### ECMP (Equal-Cost Multi-Path)
- **Mechanism**: Hash-based routing on flow 5-tuple
- **Expected**: Simple, predictable, but may create hash collisions
- **Strengths**: Low overhead, deterministic per-flow
- **Weaknesses**: May create hotspots, especially with incast patterns

### REPS (Receiver-based Path Selection)
- **Mechanism**: Receiver-driven adaptive routing
- **Expected**: Should adapt to congestion, balance load
- **Strengths**: Can react to network conditions
- **Weaknesses**: More complex, overhead

### Oblivious (Random Path Selection)
- **Mechanism**: Random path selection per flow
- **Expected**: Theoretically balanced over many flows
- **Strengths**: Provably good load balance in expectation
- **Weaknesses**: Individual flows may experience variability

## Simulation Parameters

```bash
Nodes: 128
Queue Type: composite_ecn (ECN-enabled)
Queue Size: 100 packets
ECN Thresholds: 20% (low), 80% (high)
Paths: 200 (path permutations)
Initial CWND: 1 packet
MTU: 1500 bytes
End Time: 2000 microseconds
Log Interval: 100 microseconds
Congestion Control: DCTCP
Seed: 42 (reproducible results)
```

## Troubleshooting

### Simulation Fails
- **Check**: Executable exists: `../../htsim_uec`
- **Solution**: Compile project (see Prerequisites)

### No Queue Data
- **Check**: Binary log files (`logout_*.dat`) exist
- **Check**: `parse_output` executable exists
- **Solution**: Compile with `make parse_output`

### FCT Analysis Shows No Flows
- **Check**: Simulation completed successfully
- **Check**: Output files contain "DCTCP" events
- **Possible Issue**: Simulation time too short for large flows

### Parse Output Not Found
- **Solution**: Compile parse_output:
```bash
cd ../../build
make parse_output
```

## Extending the Experiment

### Modify Traffic Pattern
Edit `congestion_scenario.cm`:
- Add more flows
- Change flow sizes
- Adjust start times
- Create different incast patterns

### Test Different Topologies
Change `TOPOLOGY` variable in `run_congestion_experiments.sh`

### Adjust Simulation Parameters
Modify parameters in `run_congestion_experiments.sh`:
- Queue size (`-q`)
- ECN thresholds (`-ecn`)
- Simulation time (`-end`)
- Number of paths (`-paths`)

## Questions to Answer

Based on your results, answer these questions:

1. **Which load balancing algorithm achieved the best mean FCT?**
   - Why do you think this algorithm performed best?

2. **Which algorithm had the lowest queue variance?**
   - What does this tell you about its load balancing effectiveness?

3. **How do the algorithms handle incast patterns?**
   - Compare FCT variance within incast groups
   - Which algorithm spreads load most evenly?

4. **Are there trade-offs between FCT and queue variance?**
   - Does optimizing for one metric hurt the other?

5. **How does the congestion scenario stress the algorithms?**
   - Which traffic patterns cause the most problems?
   - Do any algorithms show particular weaknesses?

6. **Which algorithm would you recommend for a datacenter?**
   - Consider both performance and complexity
   - What are the deployment trade-offs?

## References

- Task 1: Basic load balancing comparison
- Task 2: Queue usage logging
- Task 3: Link failure scenarios

## Contact

If you encounter issues, check:
1. All prerequisites are met
2. Scripts have execute permissions
3. Topology and connection matrix files exist
4. Previous tasks ran successfully (for reference)
