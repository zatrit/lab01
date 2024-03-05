from dataclasses import dataclass
import pygame


@dataclass
class RenderProps:
    """Свойства для рендеринга спрайта"""
    flip_x: bool = False
    flip_y: bool = False
    angle: int = 0

    def apply(self, image: pygame.Surface) -> pygame.Surface:
        image = pygame.transform.flip(image, self.flip_x, self.flip_y)
        if self.angle:
            image = pygame.transform.rotate(image, self.angle)
        return image
