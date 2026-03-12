def paint_fence(n: int, k: int) -> int:
    """
    Calculate the number of ways to paint a fence with n posts and k colors
    such that at most 2 adjacent posts have the same color.

    Args:
        n (int): Number of fence posts.
        k (int): Number of colors.

    Returns:
        int: Number of valid ways to paint the fence.
    """
    if n == 0 or k == 0:
        return 0
    if n == 1:
        return k

    # dp[i][0] = number of ways to paint i posts where the last two posts have different colors
    # dp[i][1] = number of ways to paint i posts where the last two posts have the same color
    dp = [[0, 0] for _ in range(n + 1)]

    # Base cases
    dp[1][0] = k  # Only one post, no adjacent posts, so last two different count = k
    dp[1][1] = 0  # Can't have two adjacent same colors with only one post

    for i in range(2, n + 1):
        # Last two posts have different colors:
        # We can paint the ith post with any color different from (i-1)th post color
        dp[i][0] = (dp[i - 1][0] + dp[i - 1][1]) * (k - 1)

        # Last two posts have the same color:
        # Only possible if (i-1)th and (i-2)th posts had different colors,
        # so that we don't have more than 2 adjacent same colors
        dp[i][1] = dp[i - 1][0] * 1  # paint ith post same as (i-1)th post

    return dp[n][0] + dp[n][1]