import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# load data
smartt = pd.read_csv("core_link_bytes_smartt.csv")
conga = pd.read_csv("core_link_bytes_smartt_conga.csv")

# sort for aligned comparison
smartt = smartt.sort_values("link_name").reset_index(drop=True)
conga  = conga.sort_values("link_name").reset_index(drop=True)

# sanity check
assert all(smartt["link_name"] == conga["link_name"])

# relative utilization
smartt_util = smartt["total_bytes"] / smartt["total_bytes"].mean()
conga_util  = conga["total_bytes"]  / conga["total_bytes"].mean()

# ===== Bar chart =====
x = np.arange(len(smartt))
width = 0.35

plt.figure(figsize=(10, 4))
plt.bar(x - width/2, smartt_util, width, label="SmartT")
plt.bar(x + width/2, conga_util,  width, label="SmartT-CONDA")

plt.xticks(x, smartt["link_name"], rotation=45)
plt.ylabel("Normalized Link Utilization")
plt.title("Core Link Utilization Comparison")
plt.legend()
plt.tight_layout()
plt.show()

# ===== Variance / Std =====
print("SmartT:")
print("  mean =", smartt_util.mean())
print("  std  =", smartt_util.std())
print("  var  =", smartt_util.var())

print("\nSmartT-CONDA:")
print("  mean =", conga_util.mean())
print("  std  =", conga_util.std())
print("  var  =", conga_util.var())
