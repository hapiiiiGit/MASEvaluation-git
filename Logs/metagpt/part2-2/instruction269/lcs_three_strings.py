def lcs_three_strings(X: str, Y: str, Z: str) -> int:
    """
    Find the length of the longest common subsequence of three strings.

    Args:
        X (str): First string.
        Y (str): Second string.
        Z (str): Third string.

    Returns:
        int: Length of the longest common subsequence among X, Y, and Z.
    """
    m, n, o = len(X), len(Y), len(Z)
    # Create a 3D DP array to store lengths of LCS for substrings
    dp = [[[0] * (o + 1) for _ in range(n + 1)] for __ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            for k in range(1, o + 1):
                if X[i - 1] == Y[j - 1] == Z[k - 1]:
                    dp[i][j][k] = dp[i - 1][j - 1][k - 1] + 1
                else:
                    dp[i][j][k] = max(
                        dp[i - 1][j][k],
                        dp[i][j - 1][k],
                        dp[i][j][k - 1]
                    )
    return dp[m][n][o]


def test_lcs_three_strings():
    # Test cases with expected results
    test_cases = [
        ("abcd1e2", "bc12ea", "bd1ea", 3),  # LCS is "b1e"
        ("geeks", "geeksfor", "geeksforgeeks", 5),  # LCS is "geeks"
        ("abc", "abc", "abc", 3),  # LCS is "abc"
        ("abc", "def", "ghi", 0),  # No common subsequence
        ("aab", "azb", "acb", 2),  # LCS is "ab"
        ("xyz", "xyz", "xyz", 3),  # LCS is "xyz"
        ("", "abc", "abc", 0),  # One empty string
        ("abc", "", "abc", 0),  # One empty string
        ("abc", "abc", "", 0),  # One empty string
    ]

    for i, (X, Y, Z, expected) in enumerate(test_cases, 1):
        result = lcs_three_strings(X, Y, Z)
        assert result == expected, f"Test case {i} failed: expected {expected}, got {result}"
    print("All test cases passed.")


if __name__ == "__main__":
    test_lcs_three_strings()