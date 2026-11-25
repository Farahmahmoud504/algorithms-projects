"""Empirical analysis of insertion sort.

Times insertion sort (and merge sort for comparison) on sorted, reverse-sorted
and random inputs, then writes results/results.csv and results/plot.png.

Usage:
    python experiment.py                      # n = 100 ... 5000
    python experiment.py --sizes 100 500 1000 --repeats 2
"""
import argparse
import csv
import os
import random
import time

from insertion_sort import insertion_sort, insertion_sort_counted, merge_sort

CASES = ("sorted", "reverse", "random")


def make_input(case, n, rng):
    if case == "sorted":
        return list(range(n))
    if case == "reverse":
        return list(range(n, 0, -1))
    return [rng.randint(0, 10 * n) for _ in range(n)]


def best_time(fn, data, repeats):
    """Minimum wall time over `repeats` runs (each on a fresh copy)."""
    best = float("inf")
    for _ in range(repeats):
        copy = list(data)
        t0 = time.perf_counter()
        fn(copy)
        best = min(best, time.perf_counter() - t0)
    return best


def run(sizes, repeats, seed):
    rng = random.Random(seed)
    rows = []
    for n in sizes:
        for case in CASES:
            data = make_input(case, n, rng)
            comps, shifts = insertion_sort_counted(list(data))
            rows.append({
                "n": n,
                "case": case,
                "insertion_s": best_time(insertion_sort, data, repeats),
                "merge_s": best_time(merge_sort, data, repeats),
                "comparisons": comps,
                "shifts": shifts,
            })
            r = rows[-1]
            print(f"n={n:>5} {case:<8} insertion={r['insertion_s']*1000:9.2f} ms  "
                  f"merge={r['merge_s']*1000:7.2f} ms  "
                  f"comparisons={comps:>9,}  shifts={shifts:>9,}")
    return rows


def save_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def doubling_report(rows):
    """Ratio time(2n)/time(n): ~2 means O(n), ~4 means O(n^2)."""
    print("\nDoubling ratios for insertion sort (2 -> linear, 4 -> quadratic):")
    for case in CASES:
        pts = {r["n"]: r["insertion_s"] for r in rows if r["case"] == case}
        for n in sorted(pts):
            if 2 * n in pts:
                print(f"  {case:<8} n={n:>5} -> {2*n:>5}: x{pts[2*n]/pts[n]:.2f}")


def plot(rows, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    colors = {"sorted": "tab:green", "reverse": "tab:red", "random": "tab:blue"}
    for case in CASES:
        pts = sorted((r["n"], r["insertion_s"]) for r in rows if r["case"] == case)
        ax1.plot(*zip(*pts), "o-", label=case, color=colors[case])

    # Reference curves, scaled to touch the reverse-sorted curve at the largest n.
    ns = sorted({r["n"] for r in rows})
    big = max(ns)
    t_big = next(r["insertion_s"] for r in rows if r["n"] == big and r["case"] == "reverse")
    ax1.plot(ns, [t_big * n / big for n in ns], "--", color="gray", label="c·n  (O(n))")
    ax1.plot(ns, [t_big * (n / big) ** 2 for n in ns], ":", color="black", label="c·n²  (O(n²))")
    ax1.set(title="Insertion sort running time", xlabel="n", ylabel="seconds")
    ax1.legend()
    ax1.grid(alpha=0.3)

    for name, key, style in (("insertion sort", "insertion_s", "o-"), ("merge sort", "merge_s", "s-")):
        pts = sorted((r["n"], r[key]) for r in rows if r["case"] == "random")
        ax2.plot(*zip(*pts), style, label=name)
    ax2.set(title="Random input: insertion vs merge sort", xlabel="n", ylabel="seconds")
    ax2.legend()
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"\nSaved plot -> {path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", type=int, nargs="+",
                   default=[100, 500, 1000, 2000, 3000, 4000, 5000])
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="results")
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    rows = run(args.sizes, args.repeats, args.seed)
    save_csv(rows, os.path.join(args.out, "results.csv"))
    doubling_report(rows)
    plot(rows, os.path.join(args.out, "plot.png"))


if __name__ == "__main__":
    main()
