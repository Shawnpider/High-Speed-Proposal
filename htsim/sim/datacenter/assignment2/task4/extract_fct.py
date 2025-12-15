#!/usr/bin/env python3
"""
Extract and Analyze Flow Completion Time (FCT) for Task 4
Handles multiple concurrent flows with comprehensive statistics
"""

import sys
import os
import re
from statistics import mean, median, stdev, variance
from collections import defaultdict

def parse_connection_matrix(cm_file):
    """Parse connection matrix to get all flow information"""
    flows = []
    
    if not os.path.exists(cm_file):
        print(f"Warning: Connection matrix file not found: {cm_file}")
        return flows
    
    with open(cm_file, 'r') as f:
        for line in f:
            if '->' in line:
                parts = line.split()
                src = None
                dst = None
                flow_size = 0
                start_time_us = 0
                flow_id = None
                
                # Extract source and destination (format: "0->16")
                for part in parts:
                    if '->' in part:
                        src_dst_parts = part.split('->')
                        if len(src_dst_parts) == 2:
                            try:
                                src = int(src_dst_parts[0])
                                dst = int(src_dst_parts[1])
                            except:
                                pass
                        break
                
                # Extract other parameters
                for i, part in enumerate(parts):
                    if part == 'size' and i + 1 < len(parts):
                        flow_size = int(parts[i+1])
                    elif part == 'start' and i + 1 < len(parts):
                        start_time_us = float(parts[i+1])
                    elif part == 'id' and i + 1 < len(parts):
                        flow_id = int(parts[i+1])
                
                if src is not None and dst is not None:
                    flows.append({
                        'src': src,
                        'dst': dst,
                        'size': flow_size,
                        'start_time': start_time_us,
                        'flow_id': flow_id if flow_id else len(flows) + 1,
                        'name': f'flow_{src}_{dst}',
                        'uec_name': f'Uec_{src}_{dst}'
                    })
    
    return flows

def extract_fct_from_output(output_file, flows):
    """Extract FCT for each flow from simulation output"""
    flow_results = []
    
    if not os.path.exists(output_file):
        print(f"Error: Output file not found: {output_file}")
        return flow_results
    
    with open(output_file, 'r') as f:
        lines = f.readlines()
    
    # For each flow, find DCTCP events
    for flow in flows:
        uec_name = flow['uec_name']
        first_event_time = None
        last_event_time = None
        event_count = 0
        
        for line in lines:
            # Find DCTCP events for this flow
            # Pattern: timestamp DCTCP ... Uec_src_dst
            if uec_name in line and 'DCTCP' in line:
                match = re.search(r'^(\d+\.\d+)', line)
                if match:
                    current_time = float(match.group(1))
                    if first_event_time is None:
                        first_event_time = current_time
                    last_event_time = current_time
                    event_count += 1
        
        # Calculate FCT
        if first_event_time is not None and last_event_time is not None:
            start_time = flow['start_time'] if flow['start_time'] > 0 else first_event_time
            fct_us = last_event_time - start_time
            
            if fct_us > 0:
                # Calculate throughput
                throughput_gbps = (flow['size'] * 8) / (fct_us * 1e-6) / 1e9 if fct_us > 0 else 0
                
                flow_results.append({
                    'flow_id': flow['flow_id'],
                    'name': flow['name'],
                    'src': flow['src'],
                    'dst': flow['dst'],
                    'size_bytes': flow['size'],
                    'start_time': start_time,
                    'end_time': last_event_time,
                    'fct_us': fct_us,
                    'throughput_gbps': throughput_gbps,
                    'event_count': event_count
                })
    
    return flow_results

def categorize_flows(flow_results):
    """Categorize flows by size for detailed analysis"""
    categories = {
        'small': [],      # < 50MB
        'medium': [],     # 50-100MB
        'large': []       # > 100MB
    }
    
    for flow in flow_results:
        size_mb = flow['size_bytes'] / (1024 * 1024)
        if size_mb < 50:
            categories['small'].append(flow)
        elif size_mb < 100:
            categories['medium'].append(flow)
        else:
            categories['large'].append(flow)
    
    return categories

def identify_incast_flows(flow_results):
    """Identify incast patterns (multiple senders to same receiver)"""
    receiver_map = defaultdict(list)
    
    for flow in flow_results:
        receiver_map[flow['dst']].append(flow)
    
    incast_patterns = {}
    for dst, flows in receiver_map.items():
        if len(flows) > 1:
            incast_patterns[dst] = flows
    
    return incast_patterns

def calculate_statistics(values):
    """Calculate comprehensive statistics"""
    if not values:
        return None
    
    stats = {
        'count': len(values),
        'mean': mean(values),
        'median': median(values),
        'min': min(values),
        'max': max(values),
    }
    
    if len(values) > 1:
        stats['stdev'] = stdev(values)
        stats['variance'] = variance(values)
    else:
        stats['stdev'] = 0
        stats['variance'] = 0
    
    # Calculate percentiles
    sorted_values = sorted(values)
    stats['p50'] = sorted_values[int(len(sorted_values) * 0.50)]
    stats['p95'] = sorted_values[int(len(sorted_values) * 0.95)] if len(sorted_values) > 1 else sorted_values[0]
    stats['p99'] = sorted_values[int(len(sorted_values) * 0.99)] if len(sorted_values) > 1 else sorted_values[0]
    
    return stats

def print_flow_results(flow_results):
    """Print detailed results for each flow"""
    print("\n" + "="*70)
    print("Individual Flow Results")
    print("="*70)
    
    # Sort by flow ID
    sorted_flows = sorted(flow_results, key=lambda x: x['flow_id'])
    
    for flow in sorted_flows:
        print(f"\nFlow {flow['flow_id']}: {flow['name']}")
        print(f"  Route: {flow['src']} -> {flow['dst']}")
        print(f"  Size: {flow['size_bytes']:,} bytes ({flow['size_bytes']/(1024*1024):.2f} MB)")
        print(f"  FCT: {flow['fct_us']:.2f} us ({flow['fct_us']/1000:.2f} ms)")
        print(f"  Throughput: {flow['throughput_gbps']:.2f} Gbps")
        print(f"  Time: {flow['start_time']:.2f} -> {flow['end_time']:.2f} us")
        print(f"  DCTCP Events: {flow['event_count']}")

def print_statistics(flow_results):
    """Print comprehensive FCT statistics"""
    if not flow_results:
        print("\nNo flow completions found!")
        return
    
    fcts = [f['fct_us'] for f in flow_results]
    throughputs = [f['throughput_gbps'] for f in flow_results]
    
    stats = calculate_statistics(fcts)
    tp_stats = calculate_statistics(throughputs)
    
    print("\n" + "="*70)
    print("Overall FCT Statistics")
    print("="*70)
    print(f"  Total Flows: {stats['count']}")
    print(f"  Mean FCT: {stats['mean']:.2f} us ({stats['mean']/1000:.2f} ms)")
    print(f"  Median FCT: {stats['median']:.2f} us ({stats['median']/1000:.2f} ms)")
    print(f"  Min FCT: {stats['min']:.2f} us ({stats['min']/1000:.2f} ms)")
    print(f"  Max FCT: {stats['max']:.2f} us ({stats['max']/1000:.2f} ms)")
    print(f"  Std Dev: {stats['stdev']:.2f} us")
    print(f"  Variance: {stats['variance']:.2f}")
    print(f"  P50: {stats['p50']:.2f} us ({stats['p50']/1000:.2f} ms)")
    print(f"  P95: {stats['p95']:.2f} us ({stats['p95']/1000:.2f} ms)")
    print(f"  P99: {stats['p99']:.2f} us ({stats['p99']/1000:.2f} ms)")
    
    print("\n" + "="*70)
    print("Overall Throughput Statistics")
    print("="*70)
    print(f"  Mean Throughput: {tp_stats['mean']:.2f} Gbps")
    print(f"  Median Throughput: {tp_stats['median']:.2f} Gbps")
    print(f"  Min Throughput: {tp_stats['min']:.2f} Gbps")
    print(f"  Max Throughput: {tp_stats['max']:.2f} Gbps")

def print_category_analysis(flow_results):
    """Print analysis by flow size categories"""
    categories = categorize_flows(flow_results)
    
    print("\n" + "="*70)
    print("Analysis by Flow Size")
    print("="*70)
    
    for cat_name, flows in categories.items():
        if not flows:
            continue
        
        fcts = [f['fct_us'] for f in flows]
        stats = calculate_statistics(fcts)
        
        print(f"\n{cat_name.upper()} Flows (n={len(flows)}):")
        print(f"  Mean FCT: {stats['mean']:.2f} us ({stats['mean']/1000:.2f} ms)")
        print(f"  Median FCT: {stats['median']:.2f} us ({stats['median']/1000:.2f} ms)")
        print(f"  Min FCT: {stats['min']:.2f} us")
        print(f"  Max FCT: {stats['max']:.2f} us")

def print_incast_analysis(flow_results):
    """Print analysis of incast patterns"""
    incast_patterns = identify_incast_flows(flow_results)
    
    if not incast_patterns:
        print("\n" + "="*70)
        print("No incast patterns detected")
        print("="*70)
        return
    
    print("\n" + "="*70)
    print("Incast Pattern Analysis")
    print("="*70)
    
    for receiver, flows in incast_patterns.items():
        fcts = [f['fct_us'] for f in flows]
        stats = calculate_statistics(fcts)
        senders = [f['src'] for f in flows]
        
        print(f"\nReceiver {receiver}: {len(flows)} senders")
        print(f"  Senders: {senders}")
        print(f"  Mean FCT: {stats['mean']:.2f} us ({stats['mean']/1000:.2f} ms)")
        print(f"  Max FCT: {stats['max']:.2f} us ({stats['max']/1000:.2f} ms)")
        print(f"  FCT Variance: {stats['variance']:.2f}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 extract_fct.py <output_file> <connection_matrix_file>")
        print("\nExample:")
        print("  python3 extract_fct.py results/congestion_ecmp.out congestion_scenario.cm")
        sys.exit(1)
    
    output_file = sys.argv[1]
    cm_file = sys.argv[2]
    
    print("="*70)
    print("Flow Completion Time (FCT) Analysis - Task 4")
    print("="*70)
    print(f"Output File: {output_file}")
    print(f"Connection Matrix: {cm_file}")
    
    # Parse connection matrix
    flows = parse_connection_matrix(cm_file)
    print(f"\nExpected Flows: {len(flows)}")
    
    # Extract FCT from output
    flow_results = extract_fct_from_output(output_file, flows)
    print(f"Completed Flows: {len(flow_results)}")
    
    if not flow_results:
        print("\nWarning: No completed flows found!")
        print("This might indicate:")
        print("  - Simulation did not complete")
        print("  - Flows did not finish within simulation time")
        print("  - Output format does not match expected pattern")
        sys.exit(1)
    
    # Print analyses
    print_flow_results(flow_results)
    print_statistics(flow_results)
    print_category_analysis(flow_results)
    print_incast_analysis(flow_results)
    
    print("\n" + "="*70)
    print("Analysis Complete")
    print("="*70)

if __name__ == "__main__":
    main()
