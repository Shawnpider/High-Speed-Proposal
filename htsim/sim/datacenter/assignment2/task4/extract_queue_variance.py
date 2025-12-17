#!/usr/bin/env python3
"""
Extract and Analyze Queue Length Variance for Core Switches
Processes binary log files to calculate queue statistics
"""

import sys
import os
import subprocess
import re
from statistics import mean, median, stdev, variance
from collections import defaultdict

def find_parse_output():
    """Find parse_output executable"""
    possible_paths = [
        "../../../../build/parse_output",
        "../../../build/parse_output",
        "../../build/parse_output",
        "../../../../htsim/sim/build/parse_output"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    
    return None

def extract_queue_data(log_file, idmap_file, parse_output):
    """Extract queue usage data for core switches"""


    if not os.path.exists(log_file):
        print(f"Error: Log file not found: {log_file}")
        return {}
    
    if not os.path.exists(idmap_file):
        print(f"Error: ID map file not found: {idmap_file}")
        return {}
    
    # Run parse_output to extract queue data
    try:
        cmd = [parse_output, log_file, "-ascii", "-idmap", idmap_file]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"Warning: parse_output returned non-zero exit code: {result.returncode}")
        
        output = result.stdout
        
    except subprocess.TimeoutExpired:
        print("Error: parse_output timed out")
        return {}
    except Exception as e:
        print(f"Error running parse_output: {e}")
        return {}
    
    #CDF raw data
    raw_out = open("queue_raw_samples.csv", "w")
    raw_out.write("switch,time,queue_bytes\n")
    
    # Parse output to extract core switch queue data
    queue_data = defaultdict(list)
    
    for line in output.split('\n'):
        if 'QUEUE_APPROX' in line and 'Switch_Core' in line:
            # Extract queue information
            # Format: Time Type QUEUE_APPROX ID X Ev RANGE LastQ Y MinQ Z MaxQ W Name Switch_Core_N
            parts = line.split()
            
            try:
                # Find indices
                time_idx = 0
                lastq_idx = None
                minq_idx = None
                maxq_idx = None
                name_idx = None
                
                for i, part in enumerate(parts):
                    if part == 'LastQ' and i + 1 < len(parts):
                        lastq_idx = i + 1
                    elif part == 'MinQ' and i + 1 < len(parts):
                        minq_idx = i + 1
                    elif part == 'MaxQ' and i + 1 < len(parts):
                        maxq_idx = i + 1
                    elif part.startswith('Switch_Core_'):
                        name_idx = i
                
                if lastq_idx is not None and name_idx is not None:
                    timestamp = float(parts[time_idx])
                    last_q = int(parts[lastq_idx])
                    min_q = int(parts[minq_idx]) if minq_idx else last_q
                    max_q = int(parts[maxq_idx]) if maxq_idx else last_q
                    switch_name = parts[name_idx]
                    
                    queue_data[switch_name].append({
                        'time': timestamp,
                        'last_q': last_q,
                        'min_q': min_q,
                        'max_q': max_q
                    })

                    # NEW: dump raw queue sample for CDF
                    raw_out.write(f"{switch_name},{timestamp},{last_q}\n")
            
            except (ValueError, IndexError) as e:
                continue

    
    raw_out.close()
    return queue_data

def calculate_queue_statistics(queue_data):
    """Calculate statistics for each core switch"""
    stats = {}
    
    for switch_name, measurements in queue_data.items():
        if not measurements:
            continue
        
        last_qs = [m['last_q'] for m in measurements]
        min_qs = [m['min_q'] for m in measurements]
        max_qs = [m['max_q'] for m in measurements]
        
        # Calculate statistics
        stats[switch_name] = {
            'count': len(measurements),
            'mean': mean(last_qs),
            'median': median(last_qs),
            'min': min(last_qs),
            'max': max(last_qs),
            'stdev': stdev(last_qs) if len(last_qs) > 1 else 0,
            'variance': variance(last_qs) if len(last_qs) > 1 else 0,
            'overall_min': min(min_qs),
            'overall_max': max(max_qs),
            'range': max(max_qs) - min(min_qs)
        }
    
    return stats

def calculate_overall_variance(stats):
    """Calculate variance AMONG switches (spatial variance) for load balancing metric"""
    if not stats:
        return None
    
    # Get mean queue length for each switch (represents load on that switch)
    all_means = [s['mean'] for s in stats.values()]
    
    # Variance AMONG switches (how evenly distributed is the load?)
    variance_among_switches = variance(all_means) if len(all_means) > 1 else 0
    stdev_among_switches = stdev(all_means) if len(all_means) > 1 else 0
    
    # Also keep temporal variance info for reference
    all_temporal_variances = [s['variance'] for s in stats.values()]
    
    return {
        'total_switches': len(stats),
        # NEW: Spatial variance (load balancing metric)
        'variance_among_switches': variance_among_switches,
        'stdev_among_switches': stdev_among_switches,
        # Statistics of mean queue lengths across switches
        'mean_queue_length': mean(all_means),
        'median_queue_length': median(all_means),
        'min_queue_length': min(all_means),
        'max_queue_length': max(all_means),
        'range_queue_length': max(all_means) - min(all_means),
        # Peak queue observed
        'max_queue_observed': max([s['max'] for s in stats.values()]),
        # Temporal variance (kept for reference)
        'mean_temporal_variance': mean(all_temporal_variances),
    }

def print_switch_statistics(stats):
    """Print detailed statistics for each switch"""
    print("\n" + "="*70)
    print("Per-Switch Queue Statistics")
    print("="*70)
    
    # Sort by switch name
    sorted_switches = sorted(stats.keys())
    
    for switch_name in sorted_switches:
        s = stats[switch_name]
        print(f"\n{switch_name}:")
        print(f"  Samples: {s['count']}")
        print(f"  Mean Queue Length: {s['mean']:.2f} bytes")
        print(f"  Median Queue Length: {s['median']:.2f} bytes")
        print(f"  Queue Range: {s['min']:.0f} - {s['max']:.0f} bytes")
        print(f"  Standard Deviation: {s['stdev']:.2f} bytes")
        print(f"  Variance: {s['variance']:.2f} bytes²")
        print(f"  Overall Min: {s['overall_min']:.0f} bytes")
        print(f"  Overall Max: {s['overall_max']:.0f} bytes")
        print(f"  Total Range: {s['range']:.0f} bytes")

def print_overall_statistics(overall):
    """Print overall variance statistics - focusing on spatial variance for load balancing"""
    print("\n" + "="*70)
    print("Load Balancing Analysis - Variance Among Switches")
    print("="*70)
    print(f"  Total Core Switches: {overall['total_switches']}")
    print("")
    print("  === SPATIAL VARIANCE (Load Balancing Metric) ===")
    print(f"  Variance Among Switches: {overall['variance_among_switches']:.2f} bytes²")
    print(f"  Std Dev Among Switches: {overall['stdev_among_switches']:.2f} bytes")
    print(f"    → Lower variance = Better load balancing")
    print("")
    print("  === QUEUE LENGTH DISTRIBUTION ===")
    print(f"  Mean Queue Length: {overall['mean_queue_length']:.2f} bytes")
    print(f"  Median Queue Length: {overall['median_queue_length']:.2f} bytes")
    print(f"  Min Queue Length: {overall['min_queue_length']:.2f} bytes")
    print(f"  Max Queue Length: {overall['max_queue_length']:.2f} bytes")
    print(f"  Range: {overall['range_queue_length']:.2f} bytes")
    print(f"    → Smaller range = More uniform load")
    print("")
    print("  === CONGESTION ===")
    print(f"  Peak Queue Observed: {overall['max_queue_observed']:.2f} bytes")
    print("")
    print("  === TEMPORAL INFO (Reference) ===")
    print(f"  Mean Temporal Variance: {overall['mean_temporal_variance']:.2f} bytes²")
    print(f"    → How much queues fluctuate over time")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 extract_queue_variance.py <logout_file> <idmap_file>")
        print("\nExample:")
        print("  python3 extract_queue_variance.py results/logout_ecmp.dat results/idmap.txt")
        sys.exit(1)
    
    log_file = sys.argv[1]
    idmap_file = sys.argv[2]
    
    print("="*70)
    print("Queue Length Variance Analysis - Task 4")
    print("="*70)
    print(f"Log File: {log_file}")
    print(f"ID Map: {idmap_file}")
    
    # Find parse_output
    parse_output = find_parse_output()
    if not parse_output:
        print("\nError: parse_output executable not found")
        print("Please compile the project first:")
        print("  cd htsim/sim && mkdir -p build && cd build")
        print("  cmake .. && make parse_output")
        sys.exit(1)
    
    print(f"Using parse_output: {parse_output}")
    print("\nExtracting queue data from binary log...")
    
    # Extract queue data
    queue_data = extract_queue_data(log_file, idmap_file, parse_output)
    
    if not queue_data:
        print("\nWarning: No core switch queue data found!")
        print("This might indicate:")
        print("  - No queue usage was logged")
        print("  - Log file format is different than expected")
        print("  - No core switches in topology")
        sys.exit(1)
    
    print(f"Found data for {len(queue_data)} core switches")
    
    # Calculate statistics
    stats = calculate_queue_statistics(queue_data)
    overall = calculate_overall_variance(stats)
    
    # Print results
    print_switch_statistics(stats)
    print_overall_statistics(overall)
    
    print("\n" + "="*70)
    print("Analysis Complete")
    print("="*70)

if __name__ == "__main__":
    main()
