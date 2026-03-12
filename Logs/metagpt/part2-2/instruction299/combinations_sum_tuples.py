from itertools import combinations

def find_combinations_of_sum(tuples_list, target_sum):
    """
    Find all combinations of tuples from tuples_list whose element-wise sum equals target_sum.

    Args:
        tuples_list (list of tuple of int): List of tuples with equal length.
        target_sum (tuple of int): Target tuple sum to find combinations for.

    Returns:
        list of list of tuple: List of combinations (each combination is a list of tuples)
                               whose element-wise sum equals target_sum.
    """
    if not tuples_list:
        return []

    tuple_length = len(tuples_list[0])
    # Validate all tuples have the same length as target_sum
    if any(len(t) != tuple_length for t in tuples_list):
        raise ValueError("All tuples in the list must have the same length")
    if len(target_sum) != tuple_length:
        raise ValueError("Target sum tuple must have the same length as tuples in the list")

    results = []
    n = len(tuples_list)

    # Check combinations of all possible lengths
    for r in range(1, n + 1):
        for combo in combinations(tuples_list, r):
            # Calculate element-wise sum of tuples in combo
            summed = tuple(sum(elements) for elements in zip(*combo))
            if summed == target_sum:
                results.append(list(combo))

    return results


# Example usage:
if __name__ == "__main__":
    tuples_list = [(1, 2), (3, 4), (2, 1), (1, 1)]
    target_sum = (4, 5)
    combos = find_combinations_of_sum(tuples_list, target_sum)
    print("Combinations of tuples that sum to", target_sum, ":")
    for c in combos:
        print(c)