from typing import List

def max_product_increasing_subsequence(arr: List[int]) -> int:
    """
    Finds the maximum product formed by multiplying numbers of an increasing subsequence of the array.

    Args:
        arr: List[int] - input array of integers

    Returns:
        int - maximum product of an increasing subsequence
    """
    n = len(arr)
    if n == 0:
        return 0

    # dp[i] will store the maximum product of an increasing subsequence ending at index i
    dp = arr[:]  # Initialize with the element itself

    max_product = arr[0]

    for i in range(1, n):
        for j in range(i):
            if arr[j] < arr[i]:
                # If arr[i] can extend the increasing subsequence ending at j,
                # update dp[i] if product is greater
                product = dp[j] * arr[i]
                if product > dp[i]:
                    dp[i] = product
        if dp[i] > max_product:
            max_product = dp[i]

    return max_product