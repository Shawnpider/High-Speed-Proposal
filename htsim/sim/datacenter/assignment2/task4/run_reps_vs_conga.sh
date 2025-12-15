#!/bin/bash
set -euo pipefail

EXEC="../../../build/datacenter/htsim_uec"
TOPO="../../topologies/topo_assignment2/fat_tree_128_4os.topo"
CM="congestion_scenario.cm"
OUTDIR="$(pwd)/results"
mkdir -p "$OUTDIR"

ALGOS=("reps" "reps_smart")

for algo in "${ALGOS[@]}"; do
  echo "Running $algo..."
  "$EXEC" \
    -nodes 128 -topo "$TOPO" -tm "$CM" \
    -sender_cc_algo dctcp \
    -load_balancing_algo "$algo" \
    -queue_type composite_ecn \
    -q 100 -ecn 20 80 -paths 200 -cwnd 1 -mtu 1500 \
    -end 2000 -log switch -logtime_us 100 -seed 42 \
    > "$OUTDIR/congestion_${algo}.out" 2>&1
  [ -f logout.dat ] && mv logout.dat "$OUTDIR/logout_${algo}.dat"
  if [ -f idmap.txt ] && [ ! -f "$OUTDIR/idmap.txt" ]; then
    cp idmap.txt "$OUTDIR/idmap.txt"
  fi
done
