"""Sorting Benchmark Lab.

Compares insertion, merge, quick and Python's sorted() on sorted, reversed and
random data, then writes results/results.csv and results/plot.png.

Usage:
    python benchmark.py
    python benchmark.py --sizes 1000 10000 100000 --insertion-limit 10000
"""
import argparse
import csv
import os
import random
import time

from algorithms import ALGORITHMS

KINDS = ("sorted", "reversed", "random")


def make_input(kind, n, rng):
    if kind == "sorted":
        return list(range(n))
    if kind == "reversed":
        return list(range(n, 0, -1))
    return [rng.randint(0, n) for _ in range(n)]


def timed(fn, data, repeats):
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = fn(data)
        best = min(best, time.perf_counter() - t0)
    return best, result


def run(sizes, repeats, insertion_limit, seed):
    rng = random.Random(seed)
    rows = []
    for n in sizes:
        for kind in KINDS:
            data = make_input(kind, n, rng)
            expected = sorted(data)
            for name, fn in ALGORITHMS.items():
                if name == "insertion" and n > insertion_limit:
                    continue  # O(n^2) would take minutes at this size
                seconds, result = timed(fn, data, repeats)
                assert result == expected, f"{name} returned a wrong result"
                rows.append({"n": n, "input": kind, "algorithm": name, "seconds": seconds})
                print(f"n={n:>7} {kind:<9} {name:<10} {seconds*1000:10.2f} ms")
    return rows


def save_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["n", "input", "algorithm", "seconds"])
        w.writeheader()
        w.writerows(rows)


def plot(rows, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), sharey=True)
    for ax, kind in zip(axes, KINDS):
        for name in ALGORITHMS:
            pts = sorted((r["n"], r["seconds"]) for r in rows
                         if r["input"] == kind and r["algorithm"] == name)
            if pts:
                ax.plot(*zip(*pts), "o-", label=name)
        ax.set(title=f"{kind} input", xlabel="n", xscale="log", yscale="log")
        ax.grid(alpha=0.3, which="both")
    axes[0].set_ylabel("seconds")
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"Saved plot -> {path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", type=int, nargs="+",
                   default=[1_000, 3_000, 10_000, 30_000, 100_000])
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--insertion-limit", type=int, default=10_000,
                   help="skip insertion sort above this n")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="results")
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    rows = run(args.sizes, args.repeats, args.insertion_limit, args.seed)
    save_csv(rows, os.path.join(args.out, "results.csv"))
    plot(rows, os.path.join(args.out, "plot.png"))


if __name__ == "__main__":
    main()
