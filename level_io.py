"""Скрипт, отвечающий за сохранение и загрузку
сидов уровней в папку _saves"""

from datetime import datetime
from os import path, makedirs
from math import ceil, log2
import sys

SAVES_DIR = "_saves"
SEED_LENGTH = ceil(log2(sys.maxsize) / 8)


def save_seed(seed: int):
    makedirs(SAVES_DIR, exist_ok=True)
    dt = datetime.now()
    filename = path.join(SAVES_DIR, dt.strftime("%d_%m_%Y_%H_%M_%S.bin"))
    with open(filename, "wb") as file:
        file.write(seed.to_bytes(SEED_LENGTH))
    return filename


def load_seed(filename) -> int:
    with open(filename, "rb") as file:
        return int.from_bytes(file.read(SEED_LENGTH))
