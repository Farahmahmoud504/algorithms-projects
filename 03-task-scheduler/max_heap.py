"""Array-based max-heap priority queue (written from scratch, no heapq).

Layout (0-indexed): parent(i) = (i-1)//2, left(i) = 2i+1, right(i) = 2i+2.

Items are ranked by their `key()` method; the largest key is extracted first.
A position table (item -> index) makes INCREASE-KEY O(log n) without a search.
"""


class MaxHeap:
    def __init__(self):
        self._a = []
        self._pos = {}  # id(item) -> index in self._a

    def __len__(self):
        return len(self._a)

    def __bool__(self):
        return bool(self._a)

    def __iter__(self):
        return iter(list(self._a))

    # -- helpers -----------------------------------------------------------
    def _swap(self, i, j):
        a = self._a
        a[i], a[j] = a[j], a[i]
        self._pos[id(a[i])] = i
        self._pos[id(a[j])] = j

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self._a[i].key() <= self._a[parent].key():
                break
            self._swap(i, parent)
            i = parent

    def _sift_down(self, i):  # MAX-HEAPIFY
        n = len(self._a)
        while True:
            left, right, largest = 2 * i + 1, 2 * i + 2, i
            if left < n and self._a[left].key() > self._a[largest].key():
                largest = left
            if right < n and self._a[right].key() > self._a[largest].key():
                largest = right
            if largest == i:
                return
            self._swap(i, largest)
            i = largest

    # -- public operations --------------------------------------------------
    def insert(self, item):
        """INSERT: O(log n)."""
        self._a.append(item)
        self._pos[id(item)] = len(self._a) - 1
        self._sift_up(len(self._a) - 1)

    def peek(self):
        """MAXIMUM: O(1)."""
        if not self._a:
            raise IndexError("peek from empty heap")
        return self._a[0]

    def extract_max(self):
        """EXTRACT-MAX: O(log n)."""
        if not self._a:
            raise IndexError("extract from empty heap")
        top = self._a[0]
        last = self._a.pop()
        del self._pos[id(top)]
        if self._a:
            self._a[0] = last
            self._pos[id(last)] = 0
            self._sift_down(0)
        return top

    def increase_key(self, item, new_priority):
        """INCREASE-KEY: raise item.priority, then restore the heap. O(log n)."""
        if new_priority < item.priority:
            raise ValueError("new priority is lower than current priority")
        item.priority = new_priority
        self._sift_up(self._pos[id(item)])

    def is_valid(self):
        """Check the max-heap property (used by the tests)."""
        return all(self._a[(i - 1) // 2].key() >= self._a[i].key()
                   for i in range(1, len(self._a)))
