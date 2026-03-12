def min_swaps_to_convert(s1: str, s2: str) -> int:
    """
    Count the minimum number of swaps required to convert binary string s1 to s2.
    Both strings must be of the same length and have the same number of '0's and '1's,
    otherwise conversion is impossible.

    A swap exchanges two characters at different positions in s1.

    Args:
        s1 (str): The initial binary string.
        s2 (str): The target binary string.

    Returns:
        int: The minimum number of swaps required to convert s1 to s2.

    Raises:
        ValueError: If s1 and s2 have different lengths or different character counts.
    """
    if len(s1) != len(s2):
        raise ValueError("Strings must be of the same length")

    if s1.count('0') != s2.count('0') or s1.count('1') != s2.count('1'):
        raise ValueError("Strings must have the same number of '0's and '1's")

    # Positions where s1 and s2 differ
    diff_positions = [i for i in range(len(s1)) if s1[i] != s2[i]]

    # Count how many mismatches are '0' in s1 and '1' in s2 and vice versa
    zero_to_one = 0  # s1 has '0', s2 has '1'
    one_to_zero = 0  # s1 has '1', s2 has '0'

    for i in diff_positions:
        if s1[i] == '0' and s2[i] == '1':
            zero_to_one += 1
        else:
            one_to_zero += 1

    # Each swap can fix one zero_to_one mismatch and one one_to_zero mismatch
    # So minimum swaps is max(zero_to_one, one_to_zero)
    # Since total mismatches are equal, zero_to_one == one_to_zero
    # So minimum swaps = zero_to_one (or one_to_zero)
    return zero_to_one