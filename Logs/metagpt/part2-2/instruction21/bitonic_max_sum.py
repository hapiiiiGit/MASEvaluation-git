def max_sum_bitonic_subsequence(arr):
    """
    Finds the maximum sum of a bitonic subsequence in the given array.
    A bitonic subsequence first strictly increases and then strictly decreases.

    Args:
        arr (List[int]): The input array.

    Returns:
        int: The maximum sum of a bitonic subsequence.
    """
    n = len(arr)
    if n == 0:
        return 0

    # max_sum_inc[i] will store the maximum sum of an increasing subsequence ending at i
    max_sum_inc = arr[:]  # Initialize with the element itself

    for i in range(1, n):
        for j in range(i):
            if arr[j] < arr[i] and max_sum_inc[j] + arr[i] > max_sum_inc[i]:
                max_sum_inc[i] = max_sum_inc[j] + arr[i]

    # max_sum_dec[i] will store the maximum sum of a decreasing subsequence starting at i
    max_sum_dec = arr[:]  # Initialize with the element itself

    for i in range(n - 2, -1, -1):
        for j in range(n - 1, i, -1):
            if arr[j] < arr[i] and max_sum_dec[j] + arr[i] > max_sum_dec[i]:
                max_sum_dec[i] = max_sum_dec[j] + arr[i]

    # Combine the two to get max sum bitonic subsequence
    max_sum = 0
    for i in range(n):
        # Subtract arr[i] once because it is counted twice in both sequences
        current_sum = max_sum_inc[i] + max_sum_dec[i] - arr[i]
        if current_sum > max_sum:
            max_sum = current_sum

    return max_sum