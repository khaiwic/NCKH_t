"""Đối chiếu với BFS độc lập vì ví dụ có chi phí cạnh bằng 1."""
import random
import unittest
from collections import deque

from code.Dijkstra.Dijkstra_algorithm import dijkstra, example_map


def bfs_distance(grid, start, goal):
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        (row, col), cost = queue.popleft()
        if (row, col) == goal:
            return cost
        for dr, dc in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            cell = row + dr, col + dc
            if (0 <= cell[0] < len(grid) and 0 <= cell[1] < len(grid[0])
                    and not grid[cell[0]][cell[1]] and cell not in seen):
                seen.add(cell)
                queue.append((cell, cost + 1))
    return None


class DijkstraTests(unittest.TestCase):
    def assert_valid_path(self, grid, start, goal, result):
        self.assertEqual(result.path[0], start)
        self.assertEqual(result.path[-1], goal)
        self.assertEqual(len(result.path) - 1, result.cost)
        for cell in result.path:
            self.assertEqual(grid[cell[0]][cell[1]], 0)
        for a, b in zip(result.path, result.path[1:]):
            self.assertEqual(abs(a[0]-b[0]) + abs(a[1]-b[1]), 1)

    def test_fixed_example(self):
        grid, start, goal = example_map()
        result = dijkstra(grid, start, goal)
        self.assertEqual(result.cost, 16)
        self.assert_valid_path(grid, start, goal, result)
        self.assertEqual(result.cost, bfs_distance(grid, start, goal))
        self.assertEqual(result, dijkstra(grid, start, goal))
        costs = [s.distances[s.current] for s in result.snapshots[1:]]
        self.assertEqual(costs, sorted(costs))
        self.assertEqual(result.snapshots[0].distances, {start: 0})

    def test_random_maps_against_bfs(self):
        rng = random.Random(2026)
        for _ in range(40):
            grid = [[int(rng.random() < .3) for _ in range(7)] for _ in range(6)]
            start, goal = (0, 0), (5, 6)
            grid[0][0] = grid[5][6] = 0
            result = dijkstra(grid, start, goal)
            self.assertEqual(result.cost, bfs_distance(grid, start, goal))
            if result.path:
                self.assert_valid_path(grid, start, goal, result)

    def test_unreachable(self):
        result = dijkstra([[0, 1, 0]], (0, 0), (0, 2))
        self.assertEqual(result.path, [])
        self.assertIsNone(result.cost)

    def test_start_is_goal(self):
        result = dijkstra([[0]], (0, 0), (0, 0))
        self.assertEqual(result.path, [(0, 0)])
        self.assertEqual(result.cost, 0)

    def test_reject_invalid_input(self):
        for grid, start, goal in (([], (0, 0), (0, 0)),
                                   ([[0], [0, 0]], (0, 0), (1, 0)),
                                   ([[0, 1]], (0, 0), (0, 1)),
                                   ([[0]], (-1, 0), (0, 0))):
            with self.assertRaises(ValueError):
                dijkstra(grid, start, goal)


if __name__ == "__main__":
    unittest.main()
