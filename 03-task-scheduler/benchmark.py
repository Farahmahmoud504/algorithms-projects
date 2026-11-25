"""Heap priority queue vs a sorted list that is re-sorted after every insert.

Workload: insert n random tasks one by one, then extract all of them.
Writes results/results.csv and results/plot.png.
"""
import argparse
import csv
import os
import random
import time

from max_heap import MaxHeap
from scheduler import Task


def with_heap(tasks):
    h = MaxHeap()
    for t in tasks:
        h.insert(t)
    while h:
        h.extract_max()


def with_sorted_list(tasks):
    lst = []
    for t in tasks:
        lst.append(t)
        lst.sort(key=Task.key)  # re-sort after every insert
    while lst:
        lst.pop()  # largest key is at the end


def make_tasks(n, rng):
    return [Task(f"T{i}", rng.randint(1, 1000), arrival=i) for i in range(n)]


def timed(fn, n, seed, repeats):
    best = float("inf")
    for r in range(repeats):
        tasks = make_tasks(n, random.Random(seed + r))
        t0 = time.perf_counter()
        fn(tasks)
        best = min(best, time.perf_counter() - t0)
    return best


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", type=int, nargs="+", default=[500, 1000, 2000, 4000, 8000, 16000])
    p.add_argument("--repeats", type=int, default=2)
    p.add_argument("--out", default="results")
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)

    rows = []
    for n in args.sizes:
        h = timed(with_heap, n, 1, args.repeats)
        s = timed(with_sorted_list, n, 1, args.repeats)
        rows.append({"n": n, "heap_s": h, "sorted_list_s": s})
        print(f"n={n:>6}  heap={h*1000:9.1f} ms   sorted list={s*1000:9.1f} ms   x{s/h:5.1f}")

    with open(os.path.join(args.out, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ns = [r["n"] for r in rows]
    ax.plot(ns, [r["heap_s"] for r in rows], "o-", label="max-heap  (n inserts + n extracts)")
    ax.plot(ns, [r["sorted_list_s"] for r in rows], "s-", label="sorted list, re-sort after each insert")
    ax.set(xlabel="number of tasks n", ylabel="seconds", title="Priority queue: heap vs re-sorted list")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(args.out, "plot.png")
    fig.savefig(path, dpi=150)
    print(f"Saved plot -> {path}")


if __name__ == "__main__":
    main()
