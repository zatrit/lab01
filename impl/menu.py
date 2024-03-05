import random

import pygame
import pygame_gui
from pygame_gui.core.utility import create_resource_path
from pygame_gui.elements import UIButton
from pygame_gui.windows import UIFileDialog

from game import Game, global_event, process_ui_events
from impl.level import level
from level_io import SAVES_DIR, load_seed
from util import foreach, play_music


def main_menu(game: Game):
    pygame.mouse.set_visible(True)
    screen = game.screen
    play_music(f'assets/sound/music/menu-{random.randint(1, 3)}.mp3',
               loops=-1, fade_ms=1000)

    menu_back = pygame.image.load(
        f"assets/media/menu-bg-{random.randint(1, 3)}.svg")

    manager = pygame_gui.UIManager(
        screen.get_size(), "assets/data/menu_theme.json")

    anchors = {'left': 'left', 'bottom': 'bottom'}

    play_button = UIButton(
        relative_rect=pygame.Rect(50, -240, 300, 50),
        text='Играть', manager=manager,
        anchors=anchors)  # type: ignore

    export_button = UIButton(
        relative_rect=pygame.Rect(50, -170, 300, 50),
        text='Загрузить уровень', manager=manager,
        anchors=anchors)  # type: ignore

    exit_button = UIButton(
        relative_rect=pygame.Rect(50, -100, 300, 50),
        text='Выйти', manager=manager,
        anchors=anchors)  # type: ignore

    clock = pygame.time.Clock()
    run = True
    while run:
        elapsed = clock.tick(60) / 1000.0
        events = pygame.event.get()
        foreach(lambda e: global_event(game, e), events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == play_button:
                    level(game)
                if event.ui_element == exit_button:
                    pygame.quit()
                if event.ui_element == export_button:
                    UIFileDialog(pygame.Rect(160, 50, 440, 500),
                                 manager=manager,
                                 window_title="Выберите сохранение",
                                 initial_file_path=SAVES_DIR,
                                 allow_picking_directories=False)
            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                filename = create_resource_path(event.text)
                level(game, load_seed(filename))
        process_ui_events(game, manager, events)
        manager.update(elapsed)

        scr_w, scr_h = screen.get_size()
        back_image = pygame.transform.scale(menu_back, (scr_w, scr_h))

        screen.blit(back_image, (0, 0))
        manager.draw_ui(screen)

        pygame.display.update()
