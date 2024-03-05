"""Сложный алгоритм расстановки кустов"""

from random import randint
from typing import Any, Union

# LRTB это LEFT-RIGHT-TOP-BUTTON
LRTB_KEY = Union[tuple[bool, bool, bool, bool], tuple[int, int, int, int]]


def central_bush_tile():
    return randint(14, 16) if randint(0, 40) else 17


lrtb: dict[LRTB_KEY, Any] = {
    (1, 0, 0, 0): 21,
    (0, 1, 0, 0): 20,
    (0, 0, 1, 0): lambda: randint(8, 9),
    (0, 0, 0, 1): lambda: randint(2, 3),
    (1, 0, 0, 1): 13,
    (0, 1, 0, 1): 12,
    (1, 0, 1, 0): 19,
    (0, 1, 1, 0): 18,
    (0, 0, 1, 1): lambda: randint(24, 25),
    (1, 0, 1, 1): 26,
    (0, 1, 1, 1): 27,
    (1, 1, 0, 0): lambda: randint(30, 31),
    (1, 1, 0, 1): 32,
    (1, 1, 1, 0): 33,
}

diagonal_lrtb: dict[LRTB_KEY, Any] = {
    (0, 0, 0, 1): 1,
    (0, 0, 1, 0): lambda: randint(4, 5),
    (0, 0, 1, 1): 34,
    (0, 1, 0, 0): lambda: randint(6, 7),
    (0, 1, 0, 1): 28,
    (0, 1, 1, 0): 22,
    (0, 1, 1, 1): 12,
    (1, 0, 0, 0): lambda: randint(10, 11),
    (1, 0, 0, 1): 23,
    (1, 0, 1, 0): 29,
    (1, 0, 1, 1): 13,
    (1, 1, 0, 0): 35,
    (1, 1, 0, 1): 35,
    (1, 1, 1, 0): 19,
    (1, 1, 1, 1): central_bush_tile,
}


def bushes_for_cell(level_data, x, y):
    left = level_data[y][x - 1] == "b"
    right = level_data[y][x + 1] == "b"
    top = level_data[y - 1][x] == "b"
    bottom = level_data[y + 1][x] == "b"

    lefttop = level_data[y - 1][x - 1] == "b"
    righttop = level_data[y - 1][x + 1] == "b"
    leftbottom = level_data[y + 1][x - 1] == "b"
    rightbottom = level_data[y + 1][x + 1] == "b"

    lrtb_key = left, right, top, bottom
    diagonal_lrtb_key = lefttop, righttop, leftbottom, rightbottom

    if b := diagonal_lrtb.get(diagonal_lrtb_key, None):
        yield b() if callable(b) else b
    if b := lrtb.get(lrtb_key, None):
        yield b() if callable(b) else b
