def is_lucid_number(n: int) -> bool:
    """
    Check if a number is a lucid number.
    A lucid number is a positive integer whose digits are strictly increasing from left to right.
    For example, 123, 479, 89 are lucid numbers, but 122, 321, 455 are not.

    Args:
        n (int): The number to check.

    Returns:
        bool: True if n is a lucid number, False otherwise.
    """
    if n <= 0:
        return False
    digits = str(n)
    return all(digits[i] < digits[i + 1] for i in range(len(digits) - 1))


def get_lucid_numbers_upto(n: int) -> list[int]:
    """
    Get all lucid numbers smaller than or equal to n.

    Args:
        n (int): The upper bound integer.

    Returns:
        list[int]: List of all lucid numbers <= n.
    """
    return [num for num in range(1, n + 1) if is_lucid_number(num)]


if __name__ == "__main__":
    # Example usage
    upper_bound = 150
    lucid_nums = get_lucid_numbers_upto(upper_bound)
    print(f"Lucid numbers up to {upper_bound}:")
    print(lucid_nums)