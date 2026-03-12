import math

def is_prime(num: int) -> bool:
    """Check if a number is prime using 6k ± 1 optimization."""
    if num <= 1:
        return False
    if num <= 3:
        return True
    if num % 2 == 0 or num % 3 == 0:
        return False
    i = 5
    while i * i <= num:
        if num % i == 0 or num % (i + 2) == 0:
            return False
        i += 6
    return True

def nth_nsw_prime(n: int) -> int:
    """
    Find the nth Newman–Shanks–Williams prime number.
    
    The Newman–Shanks–Williams (NSW) numbers are defined by the recurrence:
        N_0 = 1
        N_1 = 1
        N_n = 2 * N_{n-1} + N_{n-2} for n >= 2
    
    NSW primes are NSW numbers that are prime.
    
    Args:
        n (int): The 1-based index of the NSW prime to find.
    
    Returns:
        int: The nth NSW prime number.
    """
    if n < 1:
        raise ValueError("n must be a positive integer")

    # Initial NSW numbers
    N0, N1 = 1, 1
    count = 0
    index = 0

    while True:
        if index == 0:
            candidate = N0
        elif index == 1:
            candidate = N1
        else:
            candidate = 2 * N1 + N0
            N0, N1 = N1, candidate

        if is_prime(candidate):
            count += 1
            if count == n:
                return candidate

        index += 1