from typing import Deque
import pygame
from effect import Effects, Effect
from impl.effects import effect_w, effect_h


class EffectsRender(pygame.sprite.Sprite):
    """Спрайт для отрисовки списка эффектов над существом"""

    def __init__(self, effects: Effects, unit, *group):
        super().__init__(*group)
        self.effects = effects
        self.unit = unit
        self.cached_n_effects = 0
        self.image = pygame.Surface((0, 0))
        self.rect = (0,) * 4

    def update(self, _):
        images = Deque(map(Effect.get_image, self.effects.effects_list))
        n_effects = len(images)
        if not n_effects:
            return
        x, y = self.unit.rect[:2]
        x += self.unit.rect[2] // 2

        if self.cached_n_effects != n_effects:
            del self.image
            self.image = pygame.Surface(
                (effect_w * n_effects, effect_h))
            # Делает чёрный цвет прозрачным
            self.image.set_colorkey("black")
            self.cached_n_effects = n_effects
        self.image.fill("black")
        for i, image in enumerate(images):
            self.image.blit(image, (effect_w * i, 0))
        size = img_w, _ = self.image.get_size()
        self.rect = (x - img_w // 2 + 3, y - 5, size)
