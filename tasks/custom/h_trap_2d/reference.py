import heapq


def trap_water_2d(grid):
    if not grid or not grid[0]:
        return 0
    m, n = len(grid), len(grid[0])
    if m < 3 or n < 3:
        return 0
    visited = [[False] * n for _ in range(m)]
    heap = []
    for i in range(m):
        for j in range(n):
            if i in (0, m - 1) or j in (0, n - 1):
                heapq.heappush(heap, (grid[i][j], i, j))
                visited[i][j] = True
    water = 0
    while heap:
        h, i, j = heapq.heappop(heap)
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + di, j + dj
            if 0 <= ni < m and 0 <= nj < n and not visited[ni][nj]:
                visited[ni][nj] = True
                water += max(0, h - grid[ni][nj])
                heapq.heappush(heap, (max(h, grid[ni][nj]), ni, nj))
    return water
