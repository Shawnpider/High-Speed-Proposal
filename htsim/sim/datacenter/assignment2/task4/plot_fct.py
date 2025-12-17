import re
import matplotlib.pyplot as plt
import numpy as np

# ---------- Step 1: parse one result file ----------
def parse_stats(filename):
    with open(filename, "r") as f:
        text = f.read()

    def find(pattern):
        m = re.search(pattern, text, re.S)
        return float(m.group(1)) if m else None

    stats = {}
    stats["mean_fct"] = find(r"Mean FCT:\s+([\d\.]+)\s+us")
    stats["p95_fct"]  = find(r"P95:\s+([\d\.]+)\s+us")
    stats["p99_fct"]  = find(r"P99:\s+([\d\.]+)\s+us")

    stats["mean_tput"] = find(r"Mean Throughput:\s+([\d\.]+)\s+Gbps")

    stats["small_fct"]  = find(r"SMALL Flows.*?Mean FCT:\s+([\d\.]+)\s+us")
    stats["medium_fct"] = find(r"MEDIUM Flows.*?Mean FCT:\s+([\d\.]+)\s+us")
    stats["large_fct"]  = find(r"LARGE Flows.*?Mean FCT:\s+([\d\.]+)\s+us")

    return stats


# ---------- Step 2: read two algorithms ----------
smartt = parse_stats("results/fct_reps_smart.txt")
conga  = parse_stats("results/fct_reps_smart_conga.txt")


# ---------- Step 3: plot Overall FCT ----------
labels = ["Mean", "P95", "P99"]
smartt_vals = [smartt["mean_fct"], smartt["p95_fct"], smartt["p99_fct"]]
conga_vals  = [conga["mean_fct"],  conga["p95_fct"],  conga["p99_fct"]]

x = np.arange(len(labels))
w = 0.35

plt.figure()
plt.bar(x - w/2, smartt_vals, w, label="SMaRTT-REPS")
plt.bar(x + w/2, conga_vals,  w, label="SMaRTT-REPS-CONGA")
plt.xticks(x, labels)
plt.ylabel("FCT (us)")
plt.title("Overall FCT Comparison")
plt.legend()
plt.tight_layout()
plt.show()


# ---------- Step 4: plot by flow size ----------
labels = ["Small", "Medium", "Large"]
smartt_vals = [smartt["small_fct"], smartt["medium_fct"], smartt["large_fct"]]
conga_vals  = [conga["small_fct"],  conga["medium_fct"],  conga["large_fct"]]

x = np.arange(len(labels))

plt.figure()
plt.bar(x - w/2, smartt_vals, w, label="SMaRTT-REPS")
plt.bar(x + w/2, conga_vals,  w, label="SMaRTT-REPS-CONGA")
plt.xticks(x, labels)
plt.ylabel("Mean FCT (us)")
plt.title("FCT by Flow Size")
plt.legend()
plt.tight_layout()
plt.show()


# ---------- Step 5: plot throughput ----------
plt.figure()
plt.bar(
    ["SMaRTT-REPS", "SMaRTT-REPS-CONGA"],
    [smartt["mean_tput"], conga["mean_tput"]],
)
plt.ylabel("Mean Throughput (Gbps)")
plt.title("Throughput Comparison")
plt.tight_layout()
plt.show()
