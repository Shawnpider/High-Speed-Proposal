import matplotlib.pyplot as plt


def load_ratios(filename):
    """
    Load reordering ratios from file.
    Each line: one float (reordering ratio per 10k packets)
    """
    ratios = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                ratios.append(float(line))
    return ratios


def main():
    # ===== Input files =====
    reps_file = "results/reordering_ratio_reps_smart.txt"
    conga_file = "results/reordering_ratio_reps_smart_conga.txt"

    reps = load_ratios(reps_file)
    conga = load_ratios(conga_file)

    assert len(reps) == len(conga), "REPS and CONGA length mismatch"

    x = range(len(reps))

    # ============================================================
    # Figure 1: Time-series comparison
    # ============================================================
    plt.figure(figsize=(10, 5))

    plt.plot(x, reps, marker='o', label="SmaRTT-REPS")
    plt.plot(x, conga, marker='s', label="SmaRTT-REPS-CONGA")

    plt.xlabel("Time Window (per 10,000 packets)")
    plt.ylabel("Reordering Ratio")
    plt.title("Packet Reordering Ratio Over Time")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    # ============================================================
    # Figure 2: Distribution (Box Plot)
    # ============================================================
    plt.figure(figsize=(6, 5))

    plt.boxplot(
        [reps, conga],
        labels=["SmaRTT-REPS", "SmaRTT-REPS-CONGA"],
        showfliers=True
    )

    plt.ylabel("Reordering Ratio")
    plt.title("Distribution of Packet Reordering Ratio")
    plt.grid(True, axis='y')

    plt.tight_layout()
    plt.show()

    # ============================================================
    # Print summary statistics (for proposal text)
    # ============================================================
    print("===== Reordering Ratio Summary =====")
    print(f"SmaRTT-REPS:        mean={sum(reps)/len(reps):.4f}, "
          f"min={min(reps):.4f}, max={max(reps):.4f}")
    print(f"SmaRTT-REPS-CONGA:  mean={sum(conga)/len(conga):.4f}, "
          f"min={min(conga):.4f}, max={max(conga):.4f}")


if __name__ == "__main__":
    main()
