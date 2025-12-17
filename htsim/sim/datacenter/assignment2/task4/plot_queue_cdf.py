import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================
# Configuration
# =========================
FILE_SMARTT = "results/queue_raw_samples_reps.csv"
FILE_SMARTT_CONGA = "results/queue_raw_samples_reps_conga.csv"

LABEL_SMARTT = "SmaRTT-REPS (ECN)"
LABEL_SMARTT_CONGA = "SmaRTT-REPS-CONGA (Quantized MQL)"

# =========================
# Helper function
# =========================
def compute_cdf(values):
    """Return sorted values and empirical CDF"""
    values = np.asarray(values)
    values = values[values >= 0]  # safety
    values = np.sort(values)
    cdf = np.arange(1, len(values) + 1) / len(values)
    return values, cdf

# =========================
# Load data
# =========================
df_smartt = pd.read_csv(FILE_SMARTT)
df_conga = pd.read_csv(FILE_SMARTT_CONGA)

q_smartt = df_smartt["queue_bytes"].values
q_conga = df_conga["queue_bytes"].values

x1, cdf1 = compute_cdf(q_smartt)
x2, cdf2 = compute_cdf(q_conga)

# =========================
# Plot
# =========================
plt.figure(figsize=(6, 4))

plt.plot(x1, cdf1, linewidth=2, label=LABEL_SMARTT)
plt.plot(x2, cdf2, linewidth=2, label=LABEL_SMARTT_CONGA)

plt.xscale("log")
plt.xlabel("Queue Length (bytes)")
plt.ylabel("CDF")
plt.title("CDF of Queue Length Across Core Switches")

plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.legend()

plt.tight_layout()
plt.savefig("queue_length_cdf.pdf")
plt.show()
