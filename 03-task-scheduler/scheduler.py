"""Task scheduler simulation built on the max-heap priority queue.

Higher priority number = more urgent. Ties go to the task that arrived first.
"""
import random
from dataclasses import dataclass, field

from max_heap import MaxHeap


@dataclass(eq=False)
class Task:
    name: str
    priority: int
    arrival: int = 0
    base_priority: int = field(init=False)
    last_boost: int = field(init=False)

    def __post_init__(self):
        self.base_priority = self.priority
        self.last_boost = self.arrival

    def key(self):
        # larger tuple = runs first: higher priority, then earlier arrival
        return (self.priority, -self.arrival)

    def __repr__(self):
        return f"{self.name}({self.priority})"


class Scheduler:
    """Always runs the most urgent task next.

    aging: if > 0, a task that has waited `aging` ticks since it arrived (or
    since its last boost) gets priority + 1 through INCREASE-KEY, so low
    priority tasks cannot starve.
    """

    def __init__(self, aging=0):
        self.heap = MaxHeap()
        self.aging = aging

    def submit(self, task):
        self.heap.insert(task)

    def _apply_aging(self, now):
        if not self.aging:
            return
        for task in self.heap:  # iterates over a snapshot
            if now - task.last_boost >= self.aging:
                task.last_boost = now
                self.heap.increase_key(task, task.priority + 1)

    def run_next(self, now=0):
        self._apply_aging(now)
        return self.heap.extract_max()

    def run_all(self):
        """Run every queued task; return the order."""
        order = []
        while self.heap:
            order.append(self.heap.extract_max())
        return order


def simulate(arrivals, aging=0):
    """Run one task per tick.

    arrivals: list of (tick, Task). Returns a list of (tick, task) in run order,
    where `tick` is when the task started running.
    """
    arrivals = sorted(arrivals, key=lambda x: x[0])
    scheduler = Scheduler(aging=aging)
    log, i, tick = [], 0, 0
    while i < len(arrivals) or scheduler.heap:
        while i < len(arrivals) and arrivals[i][0] <= tick:
            scheduler.submit(arrivals[i][1])
            i += 1
        if scheduler.heap:
            log.append((tick, scheduler.run_next(tick)))
        tick += 1
    return log


def random_tasks(n, seed=1, max_priority=10):
    rng = random.Random(seed)
    return [Task(f"T{i+1:02d}", rng.randint(1, max_priority)) for i in range(n)]
