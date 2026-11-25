"""Demos: the slide example, 20 random tasks, and starvation vs aging."""
from scheduler import Scheduler, Task, random_tasks, simulate


def slide_example():
    print("== Example from the lecture: A(3), B(9), C(5), D(7) ==")
    s = Scheduler()
    for t in (Task("A", 3), Task("B", 9), Task("C", 5), Task("D", 7)):
        s.submit(t)
    print("Run order:", " -> ".join(t.name for t in s.run_all()), "\n")


def twenty_random():
    print("== 20 random tasks (seed 1) ==")
    s = Scheduler()
    tasks = random_tasks(20)
    for t in tasks:
        s.submit(t)
    print("Submitted:", ", ".join(map(repr, tasks)))
    print("Run order:", ", ".join(map(repr, s.run_all())), "\n")


def starvation_demo():
    print("== Starvation vs aging ==")
    print("'LOW' (priority 1) arrives at tick 0; a new urgent task (priority 5)")
    print("arrives every tick for 12 ticks.\n")

    def workload():
        low = Task("LOW", 1, arrival=0)
        urgent = [(t, Task(f"U{t:02d}", 5, arrival=t)) for t in range(12)]
        return [(0, low)] + urgent

    for aging in (0, 2):
        label = "no aging" if aging == 0 else f"aging every {aging} ticks"
        log = simulate(workload(), aging=aging)
        start = next(tick for tick, t in log if t.name == "LOW")
        print(f"{label:<22}: LOW starts at tick {start}")
        print("   order:", " ".join(t.name for _, t in log))
    print()


if __name__ == "__main__":
    slide_example()
    twenty_random()
    starvation_demo()
