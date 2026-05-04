"""Prompt templates. Centralized so prompt-engineering variants are a one-file change."""

# Wording is preserved from the original LLM-GPT-Sort tooling so results are
# directly comparable to the paper.

SORT_SYSTEM = (
    "Response should only contain the sorted data in the direction specified by the user. "
    "Do not say anything else, just return a structure with the sorted information. "
    "You role is to only return the data."
)
SORT_USER = (
    "Sort the elements in the given collection in the Ascending order, and return only "
    "the sorted collection in the list format:\n{items}"
)

SEARCH_SYSTEM = (
    "Response should only contain the data specified by the user. "
    "Do not say anything else, just return the correct index as an integer. "
    "You role is to only return the number."
)
SORTED_SEARCH_USER = (
    "Given a sorted list of numbers {items}, return the zero-based index of the number "
    "{target} in the list or -1 if the number isn't in the list."
)
UNSORTED_SEARCH_USER = (
    "Given a list of numbers {items}, return the zero-based index of the number {target} "
    "in the list or -1 if the number isn't in the list."
)

SSP_SYSTEM = (
    "Response should only contain the data specified by the user obtained by solving the "
    "subset sum problem. Do not say anything else, just return a list with the answer "
    "information. You role is to only return the data. Make sure the answer is correct."
)
SSP_USER = (
    "According to the subset sum NP problem, return the elements that sum to {goal} from "
    "the set {items} and return only the answer in the list format. "
    "Think step by step. Double check the answer."
)

SUBSTRING_SYSTEM = (
    "Response should only contain the data specified by the user. Do not say anything else, "
    "just return the answer. You role is to only return the answer."
)
SUBSTRING_USER = (
    "Given the string [{text}], return the longest palindrome substring of the string "
    "without brackets. The substring must be a palindrome."
)

GENERATE_NUMS_SYSTEM = (
    "Response should only contain the data in the range specified by the user. "
    "Do not say anything else, just return a list with the randomly generated {n} numbers "
    "data and nothing else. Do not use ellipses."
)
GENERATE_NUMS_USER = (
    "Randomly generate {n} numbers in the range 0 to {max_value}, and return only the "
    "collection in the list format. Make sure to generate exactly {n} numbers. "
    "I found you tend to generate fewer than requested so please generate more."
)
