from typing import List

def max_sum_increasing_subsequence_with_k(arr: List[int], i: int, k: int) -> int:
    """
    Find the maximum sum of an increasing subsequence that:
    - is formed from the prefix arr[0..i] (0-based index),
    - and includes the element arr[k] (with k > i),
    - and the subsequence is strictly increasing.

    Parameters:
    arr (List[int]): The input array of integers.
    i (int): The prefix end index (inclusive).
    k (int): The index of the element that must be included (k > i).

    Returns:
    int: The maximum sum of such an increasing subsequence.
         Returns 0 if no valid subsequence exists.
    """
    n = len(arr)
    if not (0 <= i < n) or not (i < k < n):
        # Invalid indices
        return 0

    # Step 1: Compute max sum increasing subsequence (MSIS) ending at each index in prefix [0..i]
    msis_prefix = [0] * (i + 1)
    for idx in range(i + 1):
        msis_prefix[idx] = arr[idx]
        for prev in range(idx):
            if arr[prev] < arr[idx] and msis_prefix[prev] + arr[idx] > msis_prefix[idx]:
                msis_prefix[idx] = msis_prefix[prev] + arr[idx]

    # Step 2: Compute max sum increasing subsequence starting at k (including k) to the right
    # We want the max sum increasing subsequence starting exactly at k (arr[k]) and going forward
    # We'll compute msis_suffix from k to n-1, where msis_suffix[x] = max sum increasing subsequence starting at x
    msis_suffix = [0] * n
    for idx in range(n - 1, k - 1, -1):
        msis_suffix[idx] = arr[idx]
        for nxt in range(idx + 1, n):
            if arr[nxt] > arr[idx] and msis_suffix[nxt] + arr[idx] > msis_suffix[idx]:
                msis_suffix[idx] = msis_suffix[nxt] + arr[idx]

    # Step 3: Combine prefix subsequence ending at some index j (0 <= j <= i) and suffix subsequence starting at k
    # The combined subsequence must be strictly increasing:
    # arr[j] < arr[k]
    # So we find max(msis_prefix[j]) for all j with arr[j] < arr[k]
    max_prefix_sum = 0
    for j in range(i + 1):
        if arr[j] < arr[k]:
            if msis_prefix[j] > max_prefix_sum:
                max_prefix_sum = msis_prefix[j]

    # If no prefix element less than arr[k], then the subsequence is just arr[k] alone
    # But the problem states subsequence from prefix until i and including kth element,
    # so prefix subsequence can be empty (sum 0) if we consider no elements before k.
    # However, since subsequence must be increasing and include arr[k], 
    # if no prefix element < arr[k], the subsequence is just arr[k].
    # So max_prefix_sum can be 0 (empty prefix subsequence).

    # The total max sum is max_prefix_sum + (msis_suffix[k] - arr[k])
    # Because msis_suffix[k] includes arr[k], and max_prefix_sum includes prefix sum ending at some j,
    # we add them but arr[k] is counted twice, so subtract once.
    total_max_sum = max_prefix_sum + msis_suffix[k]

    return total_max_sum