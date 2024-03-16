from collections import deque
from functools import lru_cache
from itertools import cycle
from typing import Iterator, Optional

from local_config import get_property

import pygame
from pygame.mixer import music as pgmusic


def empty_func(*_):
    pass


def foreach(func, _list):
    """Быстрый метод для выполнения функции на всех
    элементах списка
    https://stackoverflow.com/q/23487307/12245612
    По моим личным замерам, быстрее чем for в полтора раза"""
    deque(map(func, _list), maxlen=0)


def play_music(file, volume=1., **play_args):
    """Функция для включения музыки, обёрнутая в try/except
    на случай, если не удастся проиграть музыку
    Причиной для создание этой функции послужил вылет игры
    на компьютерах в аудитории, так как у них нету колонок"""
    try:
        pgmusic.load(file)
        pgmusic.set_volume(volume * get_property("volume"))  # type: ignore
        pgmusic.play(**play_args)
        return True
    except Exception as err:
        print(err)
        return False


def stop_music(unload=True):
    try:
        pgmusic.stop()
        if unload:
            pgmusic.unload()
    except pygame.error:
        pass


def play_sound(sound: Optional[pygame.mixer.Sound], volume=1., **play_args):
    """Функция для включения звука, аналогичаня play_music,
    но для звука"""
    if not sound:
        return
    try:
        sound.set_volume(volume * get_property("volume"))  # type: ignore
        sound.play(**play_args)
    except Exception as err:
        print(err)


class LoopedTimer:
    def __init__(self, delays: Iterator[float], callback) -> None:
        self.cur_time = 0
        self.paused = False
        self.set_delays(delays)
        self.callback = callback

    def set_delays(self, delays: Iterator[float]):
        self.delays = cycle(delays)
        self.cur_delay = next(self.delays)

    def update(self, elapsed: float):
        if self.paused:
            return
        self.cur_time += elapsed
        while self.cur_time >= self.cur_delay:
            self.cur_time -= self.cur_delay
            self.cur_delay = next(self.delays)
            self.callback()


@lru_cache(1)
def vignette():
    return pygame.image.load("assets/sprite/vignette.png").convert_alpha()