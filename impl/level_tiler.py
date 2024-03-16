import random
from dataclasses import dataclass
from itertools import product

import pygame
from typing import Optional

from generator import FLOOR_CELLS, WALL_CELLS
from impl.bushes import bushes_for_cell, central_bush_tile
from impl.terminal import TerminalType, UpgradeTerminal
from render import RenderProps

CELL_SIZE = 16
TERMINALS = {"t": TerminalType.BAT, "T": TerminalType.CHAR}


def get_cell(pos, level: list[str]):
    x, y = pos
    row = level[y] if len(level) > y else []
    return row[x] if len(row) > x else " "


@dataclass
class Tiles:
    image: pygame.Surface
    tiles: list[pygame.Surface]
    tile_width: int
    tile_height: int

    @staticmethod
    def from_image(image: pygame.Surface, size: tuple[int, int]):
        image = image.convert_alpha()
        tile_width, tile_height = size
        img_width, img_height = image.get_size()
        tiles: list[pygame.Surface] = []

        for y, x in product(range(img_height // tile_height), range(img_width // tile_width)):
            x2, y2 = x * tile_width, y * tile_height
            tiles.append(image.subsurface(
                (x2, y2, tile_width, tile_height)))
        return Tiles(image, tiles, tile_width, tile_height)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type: int, pos_x, pos_y, tiles: Tiles, *groups, render_props: Optional[RenderProps] = None):
        super().__init__(*groups)
        self.image = tiles.tiles[tile_type]
        if render_props:
            self.image = render_props.apply(self.image)
        self.rect = self.image.get_rect().move(
            tiles.tile_width * pos_x, tiles.tile_height * pos_y)


def tile_level(level_width, level_height, level_data, wall_group,
               tile_group, bush_group, interaction_group, overlay_group, timer_group):
    BUSH = Tiles.from_image(pygame.image.load(
        "assets/sprite/bushes-tiles.png").convert_alpha(), (CELL_SIZE, CELL_SIZE))
    WALL = Tiles.from_image(pygame.image.load(
        "assets/sprite/wall-tiles.png").convert_alpha(), (CELL_SIZE, CELL_SIZE))
    GROUND = Tiles.from_image(pygame.image.load(
        "assets/sprite/ground-tiles.png").convert(), (CELL_SIZE, CELL_SIZE))

    for y, x in product(range(level_height), range(level_width)):
        wall_groups = wall_group, tile_group
        current_tile = level_data[y][x]
        if level_data[y][x] in ".GTt":
            tile = random.randint(0, len(GROUND.tiles) - 2)
            tile = tile if random.randint(0, 100) else 8
            tile = tile if random.randint(0, 3) else 4
            Tile(tile, x, y, GROUND, tile_group)
        if current_tile in ".Tt":
            for tile in bushes_for_cell(level_data, x, y):
                Tile(tile, x, y, BUSH, tile_group)
        if current_tile == "b":
            Tile(central_bush_tile(), x, y, BUSH, tile_group, bush_group)
        elif current_tile.lower() == "t":
            # Создаёт терминал прокачки
            x1, y1 = map(CELL_SIZE.__mul__, (x, y))
            y1 -= CELL_SIZE
            UpgradeTerminal(TERMINALS[current_tile],
                            (x1, y1), overlay_group,
                            wall_group, interaction_group,
                            timer_group=timer_group)
        elif current_tile == "G":
            # Стекло
            Tile(7, x, y, WALL, *wall_groups)
        elif current_tile == "#":
            # Стены
            if get_cell((x, y + 1), level_data) in FLOOR_CELLS:
                tile = random.randint(1, 5)
                Tile(tile, x, y, WALL, *wall_groups)
            else:
                Tile(0, x, y, WALL, wall_group)
        if get_cell((x, y + 1), level_data) in FLOOR_CELLS\
                and get_cell((x, y), level_data) in WALL_CELLS:
            Tile(6, x, y - 1, WALL, tile_group,
                 render_props=RenderProps(angle=90))
