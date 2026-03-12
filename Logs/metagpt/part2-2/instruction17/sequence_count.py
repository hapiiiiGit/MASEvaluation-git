def count_sequences(m: int, n: int) -> int:
    """
    Count the number of sequences of length n where each element is a positive integer,
    each element is >= twice the previous element, and each element <= m.

    Args:
        m (int): The maximum allowed value for any element in the sequence.
        n (int): The length of the sequence.

    Returns:
        int: The number of valid sequences.
    """
    if n == 1:
        # For sequences of length 1, any element from 1 to m is valid
        return m

    # dp[i][x] = number of sequences of length i ending with element x
    # We'll use 1-based indexing for elements from 1 to m
    dp = [0] * (m + 1)
    # Base case: sequences of length 1
    for x in range(1, m + 1):
        dp[x] = 1

    for length in range(2, n + 1):
        new_dp = [0] * (m + 1)
        # For each possible current element x, sum over all valid previous elements y
        # such that x >= 2*y
        # To optimize, for each x, previous elements y must satisfy y <= x//2
        prefix_sum = 0
        # We'll precompute prefix sums of dp to speed up summation
        # prefix_dp[i] = sum of dp[1..i]
        prefix_dp = [0] * (m + 1)
        for i in range(1, m + 1):
            prefix_dp[i] = prefix_dp[i - 1] + dp[i]

        for x in range(1, m + 1):
            max_prev = x // 2
            if max_prev >= 1:
                new_dp[x] = prefix_dp[max_prev]
            else:
                new_dp[x] = 0
        dp = new_dp

    return sum(dp[1:])
