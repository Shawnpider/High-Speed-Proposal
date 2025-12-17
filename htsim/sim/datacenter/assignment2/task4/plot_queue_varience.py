import re
import matplotlib.pyplot as plt

def parse_queue_file(filename):
    switches = []
    avg_q = []
    max_q = []

    with open(filename, 'r') as f:
        content = f.read()

    blocks = content.split("Switch_Core_")
    for block in blocks[1:]:
        lines = block.splitlines()
        switch_id = int(lines[0].replace(":", "").strip())

        mean_match = re.search(r"Mean Queue Length:\s+([\d.]+)", block)
        max_match = re.search(r"Overall Max:\s+([\d.]+)", block)

        if mean_match and max_match:
            switches.append(switch_id)
            avg_q.append(float(mean_match.group(1)))
            max_q.append(float(max_match.group(1)))

    return switches, avg_q, max_q


# ====== Load data ======
reps_file = "results/queue_variance_reps_smart.txt"
conga_file = "results/queue_variance_reps_smart_conga.txt"

sw1, avg_reps, max_reps = parse_queue_file(reps_file)
sw2, avg_conga, max_conga = parse_queue_file(conga_file)

assert sw1 == sw2
switches = sw1

# ====== Plot ======
plt.figure(figsize=(12, 6))

plt.plot(switches, max_reps, marker='o', label="SmaRTT-REPS (Max Q)")
plt.plot(switches, max_conga, marker='s', label="SmaRTT-REPS-CONGA (Max Q)")

plt.plot(switches, avg_reps, linestyle='--', alpha=0.6, label="SmaRTT-REPS (Avg Q)")
plt.plot(switches, avg_conga, linestyle='--', alpha=0.6, label="SmaRTT-REPS-CONGA (Avg Q)")

plt.xlabel("Core Switch ID")
plt.ylabel("Queue Length (bytes)")
plt.title("Per-Core-Switch Queue Length Comparison\n(Max Queue Length over Path)")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
