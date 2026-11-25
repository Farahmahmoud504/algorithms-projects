import unittest

from maze_solver import (generate_maze, neighbors, parse_maze, path_cost,
                         solve_bfs, solve_dfs, solve_dijkstra)

LECTURE = "S..#\n##..\n...E"


def is_valid_path(grid, path, start, end):
    return (path[0] == start and path[-1] == end
            and all(b in set(neighbors(grid, a)) for a, b in zip(path, path[1:])))


class TestMaze(unittest.TestCase):
    def test_lecture_example(self):
        grid, s, e = parse_maze(LECTURE)
        bfs_path, _ = solve_bfs(grid, s, e)
        dfs_path, _ = solve_dfs(grid, s, e)
        self.assertEqual(len(bfs_path) - 1, 5)  # "Shortest path: 5 moves"
        self.assertTrue(is_valid_path(grid, dfs_path, s, e))

    def test_neighbors_skip_walls_and_edges(self):
        grid, s, _ = parse_maze(LECTURE)
        self.assertEqual(sorted(neighbors(grid, s)), [(0, 1)])

    def test_no_path(self):
        grid, s, e = parse_maze("S#E")
        self.assertIsNone(solve_bfs(grid, s, e)[0])
        self.assertIsNone(solve_dfs(grid, s, e)[0])
        self.assertIsNone(solve_dijkstra(grid, s, e)[0])

    def test_start_next_to_end(self):
        grid, s, e = parse_maze("SE")
        self.assertEqual(solve_bfs(grid, s, e)[0], [s, e])

    def test_bad_maze_rejected(self):
        for text in ("S.\n.", "S..", "S.x\n..E"):
            with self.assertRaises(ValueError):
                parse_maze(text)

    def test_bfs_is_shortest_and_dfs_valid_on_random_mazes(self):
        for seed in range(25):
            grid, s, e = generate_maze(21, 31, seed=seed)
            bfs_path, _ = solve_bfs(grid, s, e)
            dfs_path, _ = solve_dfs(grid, s, e)
            self.assertTrue(is_valid_path(grid, bfs_path, s, e))
            self.assertTrue(is_valid_path(grid, dfs_path, s, e))
            self.assertLessEqual(len(bfs_path), len(dfs_path))
            # Dijkstra with no mud costs 1 per move, so it must match BFS.
            dj_path, _ = solve_dijkstra(grid, s, e)
            self.assertEqual(len(dj_path), len(bfs_path))

    def test_dijkstra_avoids_mud(self):
        # The direct route crosses two mud cells: 5 moves but cost 13.
        # The detour along the bottom row is 9 moves and cost 9.
        grid, s, e = parse_maze("S.mm.E\n.####.\n......")
        bfs_path, _ = solve_bfs(grid, s, e)
        self.assertEqual(len(bfs_path) - 1, 5)
        self.assertEqual(path_cost(grid, bfs_path), 13)
        dj_path, _ = solve_dijkstra(grid, s, e)
        self.assertEqual(path_cost(grid, dj_path), 9)
        self.assertLess(path_cost(grid, dj_path), path_cost(grid, bfs_path))


if __name__ == "__main__":
    unittest.main()
