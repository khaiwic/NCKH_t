"""Kiểm tra đường đi tối ưu bằng BFS độc lập trên lưới đơn vị."""
import random
import unittest
from collections import deque

from A_Star_algorithm import a_star, dijkstra_baseline, example_map, manhattan


def bfs_distance(grid, start, goal):
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        cell, cost = queue.popleft()
        if cell == goal:
            return cost
        for dr, dc in ((0,-1), (1,0), (0,1), (-1,0)):
            nxt = cell[0]+dr, cell[1]+dc
            if (0 <= nxt[0] < len(grid) and 0 <= nxt[1] < len(grid[0])
                    and not grid[nxt[0]][nxt[1]] and nxt not in seen):
                seen.add(nxt)
                queue.append((nxt, cost+1))
    return None


class AStarTests(unittest.TestCase):
    def check_path(self, grid, start, goal, result):
        self.assertEqual(result.path[0], start)
        self.assertEqual(result.path[-1], goal)
        self.assertEqual(len(result.path)-1, result.cost)
        for row, col in result.path:
            self.assertEqual(grid[row][col], 0)
        for a, b in zip(result.path, result.path[1:]):
            self.assertEqual(abs(a[0]-b[0])+abs(a[1]-b[1]), 1)

    def test_fixed_example(self):
        grid, start, goal = example_map()
        result = a_star(grid, start, goal)
        baseline = dijkstra_baseline(grid, start, goal)
        self.assertEqual(result.cost, 16)
        self.assertEqual(result.cost, baseline.cost)
        self.assertEqual(baseline.expanded_count, 54)
        self.assertEqual(result.cost, bfs_distance(grid, start, goal))
        self.check_path(grid, start, goal, result)
        self.assertEqual(result, a_star(grid, start, goal))
        # Các ảnh chụp phải độc lập, không trỏ vào dict bị sửa ở bước sau.
        self.assertEqual(result.snapshots[0].g, {start: 0})
        self.assertEqual(result.snapshots[-1].current, goal)
        priorities = [s.g[s.current]+manhattan(s.current, goal) for s in result.snapshots[1:]]
        self.assertEqual(priorities, sorted(priorities))

    def test_random_maps_against_bfs(self):
        rng = random.Random(2026)
        for _ in range(80):
            grid = [[int(rng.random()<.3) for _ in range(8)] for _ in range(7)]
            start, goal = (0,0), (6,7)
            grid[0][0] = grid[6][7] = 0
            expected = bfs_distance(grid, start, goal)
            for algorithm in (a_star, dijkstra_baseline):
                result = algorithm(grid, start, goal)
                self.assertEqual(result.cost, expected)
                if expected is not None:
                    self.check_path(grid, start, goal, result)

    def test_unreachable(self):
        result = a_star([[0,1,0]], (0,0), (0,2))
        self.assertEqual(result.path, [])
        self.assertIsNone(result.cost)

    def test_start_is_goal(self):
        result = a_star([[0]], (0,0), (0,0))
        self.assertEqual(result.path, [(0,0)])
        self.assertEqual(result.cost, 0)

    def test_invalid_maps(self):
        for grid, start, goal in (([], (0,0), (0,0)),
                                   ([[0],[0,0]], (0,0), (1,0)),
                                   ([[0,2]], (0,0), (0,1)),
                                   ([[0,1]], (0,0), (0,1)),
                                   ([[0]], (-1,0), (0,0))):
            with self.assertRaises(ValueError):
                a_star(grid, start, goal)


if __name__ == "__main__":
    unittest.main()
