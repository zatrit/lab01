from dataclasses import dataclass

import pygame
import pygame_gui
from pygame.event import Event

from util import foreach, vignette

CAMERA_SIZE = 480, 270


@dataclass
class Game:
    """Класс, хранящиий данные игры"""
    size: tuple[int, int]
    aspects: float
    screen: pygame.Surface = None  # type: ignore
    is_fullscreen: bool = False
    clock = pygame.time.Clock()


@dataclass
class RunLoop():
    """Объект, который передаётся в UpdateData, дающий возможность остановить цикл"""
    running: bool = True

    def __bool__(self) -> bool:
        return self.running


@dataclass
class UpdateData():
    """Данный, передаваемые при обновлении всех спрайтов"""
    game: Game
    events: list[pygame.event.Event]
    elapsed: float
    update_number: int
    loop: RunLoop


@dataclass
class Camera:
    """Реализация камеры, использующая HackySpriteGroup,
    чтобы не рисовать всё на изображение,
    что улучшает производительность на больших уровнях"""
    size: tuple[int, int]
    render_size: tuple[int, int]
    bg: int = 0x24142c
    position: tuple[int, int] = 0, 0

    def follow(self, sprite: pygame.sprite.Sprite):
        """Обновляет расположение камеры,
        чтобы она центрировалась на объекте"""
        x, y, *_ = sprite.rect  # type: ignore
        w, h = self.size
        rw, rh = self.render_size[0] - w, self.render_size[1] - h
        x, y = x - w / 2, y - h / 2
        self.position = min(max(x, 0), rw - 1), min(max(y, 0), rh - 1)

    def draw(self, *groups: pygame.sprite.Group) -> pygame.Surface:
        """Рисует все группы на изображение"""
        surface = pygame.Surface(self.size)
        surface.fill(self.bg)
        foreach(lambda g: g.set_camera_position(self.position), groups)
        foreach(lambda g: g.draw(surface), groups)
        surface.blit(vignette(), (0, 0))
        return surface


def global_event(game: Game, event: Event):
    """Глобальный обработчик событий"""
    if event.type == pygame.QUIT or event.type == pygame.WINDOWCLOSE:
        pygame.quit()
        exit()
    if event.type == pygame.KEYDOWN:
        key_event(game, event)


def key_event(game: Game, event: Event):
    """Глобальный обработчик событий клавиатуры"""
    if event.key == pygame.K_F11:
        if game.is_fullscreen:
            pygame.display.set_mode(game.size, flags=pygame.RESIZABLE)
        else:
            game.size = game.screen.get_size()
            pygame.display.set_mode(flags=pygame.FULLSCREEN | pygame.RESIZABLE)
        game.is_fullscreen = not game.is_fullscreen


# Создаёт цикл для данной группы
def basic_loop(game: Game, *groups: pygame.sprite.Group, update_func=None, draw_func=None, camera: Camera):
    loop = RunLoop()
    update_number = 0
    while loop:
        elapsed = game.clock.tick_busy_loop(60) / 1000
        # Исправляет баг с проходом игрока через стену
        if elapsed > 0.1:
            continue
        update_number += 1
        events = pygame.event.get()
        foreach(lambda e: global_event(game, e), events)
        update_data = UpdateData(game, events, elapsed, update_number, loop)
        foreach(lambda g: g.update(update_data), groups)
        if update_func:
            update_func(update_data)
        game.screen.fill(0x110524)
        draw_scaled(game, camera.draw(*groups))
        if draw_func:
            draw_func(game.screen)
        pygame.display.update()


def draw_scaled(game: Game, surface):
    width, height = game.screen.get_size()
    offset_x, offset_y = 0, 0
    if height >= width * game.aspects:
        offset_y = (height - width * game.aspects) / 2
        height = width * game.aspects
    else:
        offset_x = (width - height / game.aspects) / 2
        width = height / game.aspects

    game.screen.blit(pygame.transform.scale(
        surface, (width, height)), (offset_x, offset_y))


def process_ui_events(game: Game, manager: pygame_gui.UIManager, events: list[Event]):
    """Обрабатывает события для UIManager"""
    for event in events:
        if event.type == pygame.WINDOWRESIZED:
            manager.set_window_resolution((event.x, event.y))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                manager.set_window_resolution(game.screen.get_size())
        manager.process_events(event)
