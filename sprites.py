from collections import deque
from functools import lru_cache
import pygame

from game import UpdateData
from util import empty_func, foreach


class Hitbox(pygame.sprite.Sprite):
    """Хитбокс для вычислений движения юнитов и т.д."""
    rect: pygame.Rect

    def __init__(self, rect, *groups):
        super().__init__(*groups)
        self.rect = rect


class SpriteTimer(pygame.sprite.Sprite):
    """Реализация таймера ввиде спрайта"""

    def __init__(self, time, callback, *groups) -> None:
        super().__init__(*groups)
        self.time, self.callback = time, callback

    def update(self, data: UpdateData):
        self.time -= data.elapsed
        if self.time <= 0:
            self.kill()
            self.callback()


class HackySpriteGroup(pygame.sprite.Group):
    """Реализация группы спрайтов для камеры из game.py"""
    offset: tuple[float, float]

    def __init__(self, *sprites) -> None:
        super().__init__(*sprites)
        self.offset = 0, 0

    def set_camera_position(self, offset: tuple[float, float]):
        self.offset = tuple(-n for n in offset) # type: ignore

    def draw_sprite(self, surface: pygame.Surface, sprite):
        pos = tuple(map(sum, zip(sprite.rect[:2], self.offset)))
        s = surface.blit(sprite.image, pos)
        del s

    def draw(self, surface: pygame.Surface) -> list[pygame.Rect]:
        sprites = self.sprites()

        foreach(lambda sprite: self.draw_sprite(surface, sprite), sprites)
        return sprites


class YOrderSpriteGroup(HackySpriteGroup):
    """Группа спрайтов, на которой объекты рисуются по порядку
    расположения по оси Y"""

    def sprites(self):
        return sorted(self.spritedict, key=lambda s: s.rect[1])


class InvisibleSpriteGroup(pygame.sprite.Group):
    """Группы спрайтов, которая не отображается и
    только принимает обновления"""
    draw = set_camera_position = empty_func  # type: ignore


class DirtySpriteGroup(HackySpriteGroup):
    @lru_cache(8)
    def surface(self):
        rects = deque(map(lambda s: s.rect, self.sprites()))
        width = max(map(lambda r: r[0] + r[2], rects))
        height = max(map(lambda r: r[1] + r[3], rects))
        surface = pygame.Surface((width, height))
        surface.set_colorkey("black")

        pygame.sprite.Group.draw(self, surface)
        return surface.convert_alpha()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface(), self.offset)
        return []
