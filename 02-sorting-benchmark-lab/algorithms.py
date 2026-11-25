"""Sorting algorithms compared in the benchmark.

Every function takes a list and returns a NEW sorted list, so the original
input can be reused for the next algorithm.
"""
import random


def insertion_sort(data):
    a = list(data)
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def merge_sort(data):
    if len(data) <= 1:
        return list(data)
    mid = len(data) // 2
    left, right = merge_sort(data[:mid]), merge_sort(data[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def quick_sort(data, seed=0):
    """In-place quicksort with a random pivot and 3-way partitioning.

    A random pivot avoids the O(n^2) behaviour on already sorted input, and the
    3-way partition keeps it fast when many values are equal. Recursing into
    the smaller side first keeps the stack depth at O(log n).
    """
    a = list(data)
    rng = random.Random(seed)

    def sort(lo, hi):
        while lo < hi:
            pivot = a[rng.randint(lo, hi)]
            lt, i, gt = lo, lo, hi
            while i <= gt:
                if a[i] < pivot:
                    a[lt], a[i] = a[i], a[lt]
                    lt += 1
                    i += 1
                elif a[i] > pivot:
                    a[i], a[gt] = a[gt], a[i]
                    gt -= 1
                else:
                    i += 1
            # a[lo:lt] < pivot, a[lt:gt+1] == pivot, a[gt+1:hi+1] > pivot
            if lt - lo < hi - gt:
                sort(lo, lt - 1)
                lo = gt + 1
            else:
                sort(gt + 1, hi)
                hi = lt - 1

    sort(0, len(a) - 1)
    return a


def python_sorted(data):
    """Python's built-in Timsort, as the reference."""
    return sorted(data)


ALGORITHMS = {
    "insertion": insertion_sort,
    "merge": merge_sort,
    "quick": quick_sort,
    "sorted()": python_sorted,
}
