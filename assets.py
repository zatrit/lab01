import json
import os
from dataclasses import dataclass
from typing import Optional

import pygame


@dataclass
class AnimationData:
    """Данные для анимации игрока и т.д."""
    image: pygame.Surface
    frames: list[pygame.Surface]
    durations: list[float]
    tags: dict[str, tuple[int, int]]

    @staticmethod
    def from_json(meta: dict, image: pygame.Surface):
        """Загружает анимацию из файла, экспортируемого Aseprite"""
        durations = [frame["duration"] / 1000 for frame in meta["frames"]]
        frames = [image.subsurface(*frame["frame"].values())
                  for frame in meta["frames"]]
        tags = dict((tag["name"], (tag["from"], tag["to"]))
                    for tag in meta["meta"]["frameTags"])
        return AnimationData(image, frames, durations, tags)


def load_animation(path: str, image_ext=".png", meta_ext=".json") -> AnimationData:
    """Загружает анимацию по имени вместе с изображением"""
    path = os.path.join("assets/sprite", path)
    image = pygame.image.load(path + image_ext).convert_alpha()
    with open(path + meta_ext, "r") as file:
        meta = json.load(file)
    return AnimationData.from_json(meta, image)


def load_sound(file) -> Optional[pygame.mixer.Sound]:
    """Загружает звук из файла"""
    try:
        return pygame.mixer.Sound(file)
    except Exception as err:
        print(err)
