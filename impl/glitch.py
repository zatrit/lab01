from abc import abstractmethod
import pygame
from assets import load_sound
from sprites import SpriteTimer
import pygame
import random

from util import empty_func, play_sound

DISAPEAR_SOUND = load_sound("assets/sound/disapeared.mp3")


class DeathAnimDummy(pygame.sprite.Sprite):
    """Спрайт, который создаётся при убийстве игрока или врага"""

    def __init__(self, rect, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = rect

    def update(self, *_):
        x, y = (random.randint(0, n - 1) for n in self.image.get_size())
        w, h = random.randint(0, self.image.get_size()[0] - x), 1
        s = self.image.copy().subsurface((x, y, w, h)).convert_alpha()
        x, y = (random.randint(0, a - b)
                for a, b in zip(self.image.get_size(), (w, h)))
        self.image.blit(s, (x, y))
        del s

    def kill(self):
        play_sound(DISAPEAR_SOUND, 0.1)
        super().kill()


class GlitchyDeath(pygame.sprite.Sprite):
    overlay_group: pygame.sprite.Group
    timer_group: pygame.sprite.Group
    rect: pygame.Rect

    @abstractmethod
    def glitchy_image(self) -> pygame.Surface:
        ...

    def kill(self):
        glitch(self.rect, self.overlay_group, self.timer_group,
               self.glitchy_image(), empty_func)
        super().kill()


def glitch(rect, group, timer_group, image, callback):
    dummy = DeathAnimDummy(rect, image, group)

    def timeout():
        callback()
        dummy.kill()
    SpriteTimer(1.75, timeout, timer_group)
