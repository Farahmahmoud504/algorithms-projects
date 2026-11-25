import random
import unittest

from max_heap import MaxHeap
from scheduler import Scheduler, Task, simulate


class TestMaxHeap(unittest.TestCase):
    def test_lecture_example(self):
        s = Scheduler()
        for t in (Task("A", 3), Task("B", 9), Task("C", 5), Task("D", 7)):
            s.submit(t)
        self.assertEqual([t.name for t in s.run_all()], ["B", "D", "C", "A"])

    def test_heap_property_and_sorted_extraction(self):
        rng = random.Random(3)
        h = MaxHeap()
        tasks = [Task(f"T{i}", rng.randint(1, 50), arrival=i) for i in range(300)]
        for t in tasks:
            h.insert(t)
            self.assertTrue(h.is_valid())
        out = []
        while h:
            out.append(h.extract_max())
            self.assertTrue(h.is_valid())
        self.assertEqual([t.key() for t in out], sorted((t.key() for t in tasks), reverse=True))

    def test_ties_go_to_earlier_arrival(self):
        h = MaxHeap()
        for i, name in enumerate("XYZ"):
            h.insert(Task(name, 5, arrival=i))
        self.assertEqual([h.extract_max().name for _ in range(3)], ["X", "Y", "Z"])

    def test_increase_key(self):
        h = MaxHeap()
        low = Task("low", 1)
        for t in (Task("a", 5), Task("b", 6), low):
            h.insert(t)
        h.increase_key(low, 10)
        self.assertTrue(h.is_valid())
        self.assertIs(h.extract_max(), low)
        with self.assertRaises(ValueError):
            h.increase_key(h.peek(), 0)

    def test_empty_heap_errors(self):
        with self.assertRaises(IndexError):
            MaxHeap().extract_max()


class TestAging(unittest.TestCase):
    def workload(self):
        low = Task("LOW", 1, arrival=0)
        return [(0, low)] + [(t, Task(f"U{t}", 5, arrival=t)) for t in range(12)]

    def start_of_low(self, aging):
        log = simulate(self.workload(), aging=aging)
        return next(tick for tick, t in log if t.name == "LOW")

    def test_without_aging_low_starves(self):
        self.assertEqual(self.start_of_low(0), 12)  # after all 12 urgent tasks

    def test_aging_lets_low_run_earlier(self):
        self.assertLess(self.start_of_low(2), 12)


if __name__ == "__main__":
    unittest.main()
