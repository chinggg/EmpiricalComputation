"""Prompt templates. Centralized so prompt-engineering variants are a one-file change."""

# Centralized System Prompt for all tasks
# Incorporating the formal definition of an Empirical Computer.
SYSTEM_PROMPT = (
    "You are an empirical computer who can solve computational problems without programming. "
    "Your will be given a natural language description of a computational problem. "
    "Please only return a single result in one-shot manner without any other text."
)

# --- Task-specific User Prompts ---

SORT_USER = "Sort the following items in ascending order and return the list: {items}"

SEARCH_SORTED_USER = (
    "In the sorted list {items}, find the zero-based index of {target}. "
    "Return the index as an integer, or -1 if not found."
)

SEARCH_UNSORTED_USER = (
    "In the list {items}, find the zero-based index of {target}. "
    "Return the index as an integer, or -1 if not found."
)

SSP_USER = (
    "Find a subset of multiset of integers {items} that sums to exactly {goal}. "
    "A solution is guaranteed to exist. If multiple subsets exist, return any one of them. "
    "Return the result as a list."
)

SUBSTRING_USER = (
    "Return the longest palindrome substring of the string [{text}] without brackets. "
    "A solution is guaranteed to exist. If multiple palindromes have the same maximum length, return any one of them."
)

GENERATE_NUMS_USER = "Generate {n} random numbers between 0 and {max_value} as a list."
