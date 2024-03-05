import random
import sys
from itertools import product

import pygame
import pygame_gui
from typing import Callable

from game import CAMERA_SIZE, Camera, Game, UpdateData, basic_loop, process_ui_events
from generator import FLOOR_CELLS, Generator, RoguelikeMap
from impl.enemy import level_grid
from impl.enemy_spawner import EnemySpawnProps, EnemySpawner
from impl.level_tiler import CELL_SIZE, tile_level
from impl.player import Player
from level_io import save_seed
from sprites import DirtySpriteGroup, HackySpriteGroup, InvisibleSpriteGroup, YOrderSpriteGroup
from util import stop_music


def level_ui(game: Game, level: RoguelikeMap, player) -> tuple[pygame_gui.UIManager, Callable]:
    manager = pygame_gui.UIManager(
        game.screen.get_size(), "assets/data/overlay_theme.json")

    minimap = pygame.Surface(level.size)
    scale = 5

    cached_cell = 0, 0

    for (y, row), x in product(enumerate(level.tiles), range(level.size[0])):
        if row[x] in FLOOR_CELLS:
            minimap.set_at((x, y), 0xC7D4E1)

    minimap = pygame.transform.scale_by(minimap, scale)
    minimap.set_colorkey((0, 0, 0, 0))
    size = tuple(map(scale.__mul__, level.size))

    img = pygame_gui.elements \
        .UIImage((25, 25, *size), minimap, manager=manager)  # type: ignore

    mp_text = pygame_gui.elements.UITextBox(
        "0 ОМ", (-85, 25, 60, 30), manager=manager, anchors={"right": "right"})
    player.mod_points_listener = lambda mp: mp_text.set_text("%d ОМ" % mp)

    health_bar = pygame_gui.elements.UIProgressBar(
        (25, -55, 300, 40), manager=manager, anchors={"bottom": "bottom"})

    def update(data: UpdateData):
        nonlocal cached_cell
        if not player.alive():
            img.set_image(minimap)
        elif cached_cell != player.get_cell():
            cached_cell = player.get_cell()
            minimap_player = minimap.copy()
            minimap_player.fill(
                0x28C074, (*map(scale.__mul__, cached_cell), scale, scale))
            img.set_image(minimap_player)
        health_bar.set_current_progress(
            player.unit_data.health / player.unit_data.max_health)

        manager.update(data.elapsed)
        process_ui_events(game, manager, data.events)

    return manager, update


def level(game: Game, seed=None):
    stop_music()
    pygame.mouse.set_visible(False)

    overlay_group = YOrderSpriteGroup()
    unit_group = YOrderSpriteGroup()
    tile_group = DirtySpriteGroup()
    interaction_group = HackySpriteGroup()

    SpriteGroup = pygame.sprite.Group
    wall_group = SpriteGroup()
    bush_group = SpriteGroup()
    enemy_group = SpriteGroup()
    player_group = SpriteGroup()

    timer_group = InvisibleSpriteGroup()

    level_size = level_width, level_height = 48, 32

    if seed is None:
        seed = random.randint(0, sys.maxsize)
        save_seed(seed)

    random.seed(seed)

    gen = Generator(*level_size, random_spurs=0, rooms_overlap=True)
    level = gen.gen_tiles_level()
    grid = level_grid(level.tiles)

    room = random.choice(level.room_list)
    local_pos = (random.randint(2, n - 2) for n in room[2:])
    room_pos = room[:2]
    pos: tuple[int, int] = tuple(map(CELL_SIZE.__mul__, map(sum, zip(local_pos, room_pos)))) # type: ignore

    player = Player(player_group, unit_group,
                    pos=pos,
                    collision_groups=(wall_group,),
                    bushes_group=bush_group,
                    overlay_group=overlay_group,
                    enemy_group=enemy_group,
                    timer_group=timer_group,
                    interaction_group=interaction_group)

    enemy_props = EnemySpawnProps(
        enemy_group, overlay_group, timer_group,
        wall_group, bush_group, player_group,
        unit_group, grid, player, level)
    EnemySpawner(enemy_props, timer_group)

    tile_level(level_width, level_height, level.tiles,
               wall_group, tile_group, bush_group,
               interaction_group, overlay_group, timer_group)

    camera = Camera(
        CAMERA_SIZE,
        render_size=(level_width * CELL_SIZE, level_height * CELL_SIZE))

    manager, ui_update = level_ui(game, level, player)

    def update(data):
        ui_update(data)
        camera.follow(player)

    basic_loop(game, timer_group, tile_group, interaction_group,
               unit_group, overlay_group,
               camera=camera,
               update_func=update,
               draw_func=manager.draw_ui)
