"""Maze Solver: BFS (shortest path), DFS (any path) and Dijkstra (mud cells).

Maze file format:
    #  wall          .  open cell          S  start          E  end
    m  mud (open, but costs 5 to enter; used by the Dijkstra extension)

The grid is an *implicit graph*: cells are vertices, and an edge joins two
open cells that touch up, down, left or right. No adjacency list is built.
Each search stores a parent for every visited cell and rebuilds the path at the
end, instead of keeping whole paths in the queue/stack.
"""
import argparse
import heapq
import random
from collections import deque

MUD_COST = 5
MOVES = ((-1, 0), (1, 0), (0, -1), (0, 1))  # up, down, left, right


# -- reading / generating -------------------------------------------------------
def parse_maze(text):
    grid = [list(line) for line in text.strip("\n").splitlines()]
    if not grid or len({len(r) for r in grid}) != 1:
        raise ValueError("maze must be a non-empty rectangle")
    start = end = None
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch not in "#.SEm":
                raise ValueError(f"unknown character {ch!r} at row {r}, column {c}")
            if ch == "S":
                start = (r, c)
            elif ch == "E":
                end = (r, c)
    if start is None or end is None:
        raise ValueError("maze needs one S and one E")
    return grid, start, end


def load_maze(path):
    with open(path, encoding="utf-8") as f:
        return parse_maze(f.read())


def generate_maze(rows, cols, seed=0, extra_openings=0.08, mud=0.0):
    """Random maze (rows and cols forced odd) carved with DFS, plus a few extra
    openings so there are loops and BFS/DFS can disagree."""
    rng = random.Random(seed)
    rows, cols = rows | 1, cols | 1
    g = [["#"] * cols for _ in range(rows)]
    stack = [(1, 1)]
    g[1][1] = "."
    while stack:
        r, c = stack[-1]
        options = [(r + dr * 2, c + dc * 2, dr, dc) for dr, dc in MOVES
                   if 0 < r + dr * 2 < rows - 1 and 0 < c + dc * 2 < cols - 1
                   and g[r + dr * 2][c + dc * 2] == "#"]
        if not options:
            stack.pop()
            continue
        nr, nc, dr, dc = rng.choice(options)
        g[r + dr][c + dc] = g[nr][nc] = "."
        stack.append((nr, nc))
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if g[r][c] == "#" and rng.random() < extra_openings:
                g[r][c] = "."
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == "." and rng.random() < mud:
                g[r][c] = "m"
    g[1][1], g[rows - 2][cols - 2] = "S", "E"
    return g, (1, 1), (rows - 2, cols - 2)


# -- graph helpers -----------------------------------------------------------------
def neighbors(grid, cell):
    """Open cells up, down, left, right of `cell`."""
    r, c = cell
    for dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != "#":
            yield (nr, nc)


def rebuild_path(parent, end):
    if end not in parent:
        return None
    path = []
    cell = end
    while cell is not None:
        path.append(cell)
        cell = parent[cell]
    return path[::-1]


# -- the three solvers ------------------------------------------------------------------
# Each returns (path or None, explored_cells_in_visit_order).
def solve_bfs(grid, start, end):
    """Queue. Finds a path with the fewest moves."""
    parent = {start: None}
    queue = deque([start])
    explored = []
    while queue:
        cell = queue.popleft()
        explored.append(cell)
        if cell == end:
            break
        for nxt in neighbors(grid, cell):
            if nxt not in parent:
                parent[nxt] = cell
                queue.append(nxt)
    return rebuild_path(parent, end), explored


def solve_dfs(grid, start, end):
    """Stack. Finds *a* path, not necessarily the shortest."""
    parent = {start: None}
    stack = [start]
    explored = []
    visited = set()
    while stack:
        cell = stack.pop()
        if cell in visited:
            continue
        visited.add(cell)
        explored.append(cell)
        if cell == end:
            break
        for nxt in neighbors(grid, cell):
            if nxt not in visited:
                parent[nxt] = cell  # last cell to push nxt; fixed once nxt is visited
                stack.append(nxt)
    return (rebuild_path(parent, end) if end in visited else None), explored


def step_cost(grid, cell):
    return MUD_COST if grid[cell[0]][cell[1]] == "m" else 1


def solve_dijkstra(grid, start, end):
    """Min-heap. Cheapest path when mud cells cost MUD_COST to enter."""
    dist = {start: 0}
    parent = {start: None}
    heap = [(0, start)]
    settled = set()
    explored = []
    while heap:
        d, cell = heapq.heappop(heap)
        if cell in settled:
            continue
        settled.add(cell)
        explored.append(cell)
        if cell == end:
            break
        for nxt in neighbors(grid, cell):
            nd = d + step_cost(grid, nxt)
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                parent[nxt] = cell
                heapq.heappush(heap, (nd, nxt))
    return rebuild_path(parent, end), explored


SOLVERS = {"bfs": solve_bfs, "dfs": solve_dfs, "dijkstra": solve_dijkstra}


def path_cost(grid, path):
    return sum(step_cost(grid, c) for c in path[1:])


# -- output ----------------------------------------------------------------------------------
def render_ascii(grid, path, start, end):
    out = [row[:] for row in grid]
    for r, c in (path or [])[1:-1]:
        out[r][c] = "*"
    return "\n".join("".join(row) for row in out)


def draw_png(grid, start, end, results, filename):
    """results: {name: (path, explored)} -> one panel per solver."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap

    code = {"#": 0, ".": 1, "m": 2, "S": 1, "E": 1}
    base = [[code[ch] for ch in row] for row in grid]
    cmap = ListedColormap(["#222222", "#ffffff", "#c8a27a"])
    fig, axes = plt.subplots(1, len(results), figsize=(5.5 * len(results), 5.5))
    if len(results) == 1:
        axes = [axes]
    for ax, (name, (path, explored)) in zip(axes, results.items()):
        ax.imshow(base, cmap=cmap, vmin=0, vmax=2)
        if explored:
            ys, xs = zip(*explored)
            ax.scatter(xs, ys, s=10, color="#9ecae1", zorder=2)
        if path:
            ys, xs = zip(*path)
            ax.plot(xs, ys, "-", color="tab:red", lw=2.5, zorder=3)
        ax.scatter([start[1]], [start[0]], s=90, color="tab:green", zorder=4)
        ax.scatter([end[1]], [end[0]], s=90, color="tab:blue", marker="*", zorder=4)
        moves = f"{len(path) - 1} moves" if path else "no path"
        ax.set_title(f"{name.upper()}: {moves}, explored {len(explored)} cells")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    print(f"Saved picture -> {filename}")


def main():
    p = argparse.ArgumentParser(description="Solve a grid maze with BFS, DFS and Dijkstra.")
    p.add_argument("maze", nargs="?", help="maze text file (omit when using --random)")
    p.add_argument("--random", nargs=2, type=int, metavar=("ROWS", "COLS"),
                   help="generate a random maze instead of reading a file")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--mud", type=float, default=0.0, help="share of open cells that are mud (random mazes)")
    p.add_argument("--algos", nargs="+", default=["bfs", "dfs"], choices=SOLVERS)
    p.add_argument("--png", help="save a picture of every solver's path and explored cells")
    p.add_argument("--no-ascii", action="store_true")
    args = p.parse_args()

    if args.random:
        grid, start, end = generate_maze(*args.random, seed=args.seed, mud=args.mud)
    elif args.maze:
        grid, start, end = load_maze(args.maze)
    else:
        p.error("give a maze file or --random ROWS COLS")

    results = {}
    for name in args.algos:
        path, explored = SOLVERS[name](grid, start, end)
        results[name] = (path, explored)
        if path is None:
            print(f"{name.upper():<9}: no path (explored {len(explored)} cells)")
            continue
        extra = f", cost {path_cost(grid, path)}" if "m" in "".join("".join(r) for r in grid) else ""
        print(f"{name.upper():<9}: {len(path) - 1} moves{extra}, explored {len(explored)} cells")
        if not args.no_ascii and len(grid[0]) <= 60:
            print(render_ascii(grid, path, start, end), "\n")
    if args.png:
        draw_png(grid, start, end, results, args.png)


if __name__ == "__main__":
    main()
