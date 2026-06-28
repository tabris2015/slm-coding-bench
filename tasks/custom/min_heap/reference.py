import heapq


class MinHeap:
    def __init__(self):
        self._h = []

    def push(self, x):
        heapq.heappush(self._h, x)

    def pop(self):
        if not self._h:
            raise IndexError("pop from empty heap")
        return heapq.heappop(self._h)

    def peek(self):
        if not self._h:
            raise IndexError("peek from empty heap")
        return self._h[0]

    def __len__(self):
        return len(self._h)
