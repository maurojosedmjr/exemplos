from typing import List


def is_palyndrome(string: str) -> bool:
    new_string_list: List[str] = []
    for c in string:
        new_string_list.insert(0, c)

    return "".join(new_string_list) == string


assert not is_palyndrome("terereu")

assert is_palyndrome("anana")


def is_palyndrome_other(string: str) -> bool:
    new_string: str = ""
    for c in string:
        new_string = c + new_string
    return new_string == string


assert not is_palyndrome_other("terereu")

assert is_palyndrome_other("anana")


def search_binary(list_of_integers: List[int], desired_int: int) -> int:
    length: int = len(list_of_integers)

    if any([length == 0, length == 1 and list_of_integers[0] != desired_int]):
        return -1
    elif length == 1:
        return 0

    mid: int = length // 2

    if list_of_integers[mid] == desired_int:
        return mid
    elif desired_int < list_of_integers[mid]:
        return search_binary(list_of_integers[:mid], desired_int)

    return search_binary(list_of_integers[mid:], desired_int) + mid


assert search_binary([2, 3, 6, 7, 10, 11], 10) == 4

assert search_binary([], 10) == -1

assert search_binary([2], 2) == 0

assert search_binary([2], 10) == -1

assert search_binary([2, 3, 6, 7, 10, 11], 3) == 1

assert search_binary([2, 3, 6, 7, 10, 11, 13], 7) == 3

assert search_binary([1], None) == -1

assert search_binary([1], -1) == -1

assert search_binary([-1], -1) == 0
