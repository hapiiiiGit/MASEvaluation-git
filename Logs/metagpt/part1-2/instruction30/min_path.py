from typing import List, Tuple
import heapq

def minPath(grid: List[List[int]], k: int) -> List[int]:
    """
    Given a grid with N rows and N columns (N >= 2) and a positive integer k,
    each cell of the grid contains a value. Every integer in the range [1, N * N]
    inclusive appears exactly once on the cells of the grid.

    You have to find the minimum path of length k in the grid. You can start
    from any cell, and in each step you can move to any of the neighbor cells,
    in other words, you can go to cells which share an edge with your current
    cell.
    Please note that a path of length k means visiting exactly k cells (not
    necessarily distinct).
    You CANNOT go off the grid.
    A path A (of length k) is considered less than a path B (of length k) if
    after making the ordered lists of the values on the cells that A and B go
    through (let's call them lst_A and lst_B), lst_A is lexicographically less
    than lst_B, in other words, there exist an integer index i (1 <= i <= k)
    such that lst_A[i] < lst_B[i] and for any j (1 <= j < i) we have
    lst_A[j] = lst_B[j].
    It is guaranteed that the answer is unique.
    Return an ordered list of the values on the cells that the minimum path go through.

    Args:
        grid: List[List[int]], the grid of values.
        k: int, the length of the path.

    Returns:
        List[int]: the lexicographically smallest path of length k.
    """
    N = len(grid)
    if N == 0 or k == 0:
        return []

    # Directions: up, down, left, right
    directions = [(-1,0), (1,0), (0,-1), (0,1)]

    # Priority queue: (path_so_far, x, y, steps)
    # path_so_far is a tuple of values, so heapq will sort lexicographically
    heap: List[Tuple[Tuple[int, ...], int, int, int]] = []

    # Start from every cell
    for i in range(N):
        for j in range(N):
            heapq.heappush(heap, ((grid[i][j],), i, j, 1))

    # Visited: (x, y, steps, path_so_far)
    # To avoid revisiting the same state with a worse path
    # We use a dict: (x, y, steps) -> best path_so_far
    visited = dict()

    while heap:
        path_so_far, x, y, steps = heapq.heappop(heap)
        if steps == k:
            return list(path_so_far)
        key = (x, y, steps)
        # Only continue if this path_so_far is better than any previously found for this state
        if key in visited and visited[key] <= path_so_far:
            continue
        visited[key] = path_so_far
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N:
                new_path = path_so_far + (grid[nx][ny],)
                heapq.heappush(heap, (new_path, nx, ny, steps + 1))

# Example usage:
if __name__ == "__main__":
    grid1 = [ [1,2,3], [4,5,6], [7,8,9]]
    k1 = 3
    print(minPath(grid1, k1))  # Output: [1, 2, 1]

    grid2 = [ [5,9,3], [4,1,6], [7,8,2]]
    k2 = 1
    print(minPath(grid2, k2))  # Output: [1]