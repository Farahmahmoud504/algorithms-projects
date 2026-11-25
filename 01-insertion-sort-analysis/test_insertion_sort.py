import random
import unittest

from insertion_sort import insertion_sort, insertion_sort_counted, merge_sort


class TestInsertionSort(unittest.TestCase):
    def test_matches_builtin(self):
        rng = random.Random(1)
        for n in (0, 1, 2, 10, 200):
            data = [rng.randint(-50, 50) for _ in range(n)]
            self.assertEqual(insertion_sort(list(data)), sorted(data))
            self.assertEqual(merge_sort(data), sorted(data))

    def test_worst_case_counts(self):
        # Reverse of n=4: n(n-1)/2 = 6 comparisons and 6 shifts.
        self.assertEqual(insertion_sort_counted([4, 3, 2, 1]), (6, 6))

    def test_best_case_counts(self):
        # Sorted n=4: n-1 = 3 comparisons and 0 shifts.
        self.assertEqual(insertion_sort_counted([1, 2, 3, 4]), (3, 0))

    def test_sorts_in_place(self):
        a = [3, 1, 2]
        insertion_sort_counted(a)
        self.assertEqual(a, [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
