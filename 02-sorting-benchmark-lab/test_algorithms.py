import random
import unittest

from algorithms import ALGORITHMS


class TestSorts(unittest.TestCase):
    def check(self, data):
        for name, fn in ALGORITHMS.items():
            original = list(data)
            self.assertEqual(fn(data), sorted(data), name)
            self.assertEqual(data, original, f"{name} modified its input")

    def test_edge_cases(self):
        for data in ([], [1], [2, 1], [1, 1, 1, 1], [5, 4, 3, 2, 1], list(range(50))):
            self.check(data)

    def test_random_with_duplicates(self):
        rng = random.Random(7)
        for n in (10, 100, 500):
            self.check([rng.randint(0, 20) for _ in range(n)])

    def test_quick_sort_large_sorted_input(self):
        # Would hit recursion limits / O(n^2) with a naive first-element pivot.
        data = list(range(20000))
        self.assertEqual(ALGORITHMS["quick"](data), data)


if __name__ == "__main__":
    unittest.main()
