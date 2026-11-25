# Algorithms: Analysis and Design — Mini Projects

One mini project from each lecture of the *Analysis of Algorithms* course (CS314).
Everything is plain Python 3 (standard library only; `matplotlib` is used just to draw the plots).

| # | Project | Lecture topic | Core idea | Folder |
|---|---------|---------------|-----------|--------|
| 1 | Empirical Analysis of Insertion Sort | Intro / asymptotic analysis | Measure O(n) best case vs O(n²) worst case | [`01-insertion-sort-analysis`](01-insertion-sort-analysis) |
| 2 | Sorting Benchmark Lab | Divide and conquer, sorting | Insertion vs merge vs quick vs `sorted()` | [`02-sorting-benchmark-lab`](02-sorting-benchmark-lab) |
| 3 | Task Scheduler | Heaps | Max-heap priority queue, INSERT / EXTRACT-MAX / INCREASE-KEY | [`03-task-scheduler`](03-task-scheduler) |
| 4 | Maze Solver | Graphs | BFS (shortest), DFS (any path), Dijkstra (weighted) | [`04-maze-solver`](04-maze-solver) |

## Setup

```bash
git clone <your-repo-url>
cd <repo-name>
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Each project folder is self-contained. Run its tests with `python -m unittest` from inside the folder,
and see its own README for the commands that reproduce the results and plots.

## Notes

* Timings depend on the machine; the *shape* of the curves (linear vs quadratic vs n log n) is what matters.
* All random inputs use fixed seeds, so counts and mazes are reproducible.
