def nth_polite_number(n: int) -> int:
    """
    Find the nth polite number.

    A polite number is a positive integer that can be expressed as the sum of
    two or more consecutive positive integers. Equivalently, polite numbers
    are all positive integers except powers of two.

    Args:
        n (int): The index (1-based) of the polite number to find.

    Returns:
        int: The nth polite number.

    Raises:
        ValueError: If n is not a positive integer.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")

    # Polite numbers are all positive integers except powers of two.
    # We iterate through positive integers, skipping powers of two,
    # until we find the nth polite number.

    count = 0
    num = 1
    while True:
        # Check if num is a power of two
        if (num & (num - 1)) != 0:
            count += 1
            if count == n:
                return num
        num += 1