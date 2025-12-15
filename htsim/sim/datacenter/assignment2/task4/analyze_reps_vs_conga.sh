#!/bin/bash
set -euo pipefail
OUTDIR="$(pwd)/results"
CM="congestion_scenario.cm"
IDMAP="$OUTDIR/idmap.txt"
[ ! -f "$IDMAP" ] && IDMAP="idmap.txt"

echo "FCT comparison"
python3 extract_fct.py "$OUTDIR/congestion_reps.out" "$CM" | tee "$OUTDIR/fct_reps.txt"
python3 extract_fct.py "$OUTDIR/congestion_reps_smart.out" "$CM" | tee "$OUTDIR/fct_reps_smart.txt"

echo "Queue variance comparison"
python3 extract_queue_variance.py "$OUTDIR/logout_reps.dat" "$IDMAP" | tee "$OUTDIR/queue_variance_reps.txt"
python3 extract_queue_variance.py "$OUTDIR/logout_reps_smart.dat" "$IDMAP" | tee "$OUTDIR/queue_variance_reps_smart.txt"

echo "Summary:"
paste <(printf "algo\nreps\nreps_smart\n") \
      <(printf "FCT_out\nfct_reps.txt\nfct_reps_smart.txt\n") \
      <(printf "Qvar_out\nqueue_variance_reps.txt\nqueue_variance_reps_smart.txt\n")
