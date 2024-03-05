from functools import lru_cache
from itertools import product
import random
from typing import Iterable, Union

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.best_first import BestFirst
from assets import load_sound

from game import UpdateData
from generator import FLOOR_CELLS, WALL_CELLS
from impl.player import Player
from impl.unit import Unit

from util import foreach, play_sound


FINDER = BestFirst(diagonal_movement=DiagonalMovement.always)
PICKUP_SOUND = load_sound("assets/sound/pickup.mp3")


class Enemy(Unit):
    """Враг, имеющий искусственный интелект"""
    see_player: bool = False
    target_pos = None

    def __init__(self, *groups, pos: tuple[int, int], collision_groups, bushes_group, overlay_group, player_group, timer_group, player, grid) -> None:
        super().__init__(*groups, pos=pos, collision_groups=collision_groups,
                         bushes_group=bushes_group, overlay_group=overlay_group,
                         timer_group=timer_group, hittable_group=player_group,
                         sprite="enemy")
        self.player: Player = player
        self.grid = grid

        foreach(self.unit_data.effects.add_effect,
                player.unit_data.effects.effects_list[random.randint(0, 1)::2])

    def get_move_direction(self, _: UpdateData) -> Union[tuple[int, int], Iterable[int]]:
        # Если бот не видит игрока, то он бездействует
        if not self.see_player or not self.player.alive():
            return 0, 0

        # Расчёт дистанции, тут не используется квадратный корень
        # так как это очень дорогая операция
        dist = sum((a - b) ** 2 for a,
                   b in zip(self.player.rect[:2], self.rect[:2]))
        if dist < 121:
            self.hit()
            return 0, 0

        target_pos = next_pos(self.grid, self.get_cell(),
                              self.player.get_cell())

        if not target_pos:
            # Режим избиения игрока
            points = zip(self.player.get_center(), self.get_center())
            return map(normalize, (a - b for a, b in points))

        target_direct = map(
            normalize, (a - b for a, b in zip(target_pos, self.get_cell())))
        return target_direct

    def kill(self):
        play_sound(PICKUP_SOUND, 0.5)
        self.player.mod_points += 1
        self.player.unit_data.health += 1
        return super().kill()


def level_grid(level: list[str]):
    matrix = [[0 for _ in range(len(level[0]))] for _ in range(len(level))]
    weights = [*WALL_CELLS, "t", "T", " ", ".", "b"]
    for x, y in product(range(len(level[0])), range(len(level))):
        c = level[y][x]
        matrix[y][x] = weights.index(c) - 3
        if c in FLOOR_CELLS:
            nearby = (level[y1][x1] for y1, x1 in product(
                range(y, y + 2), range(x - 1, x + 2)))
            if any(map(WALL_CELLS.__contains__, nearby)):
                matrix[y][x] = 0
    return Grid(matrix=matrix)


@lru_cache(128)
def next_pos(grid: Grid, _from: tuple[int, int], to: tuple[int, int]):
    if not all(0 <= a < b for a, b in zip(_from, (grid.width, grid.height))):
        return
    if not all(0 <= a < b for a, b in zip(to, (grid.width, grid.height))):
        return
    grid.cleanup()
    start = grid.node(*_from)
    end = grid.node(*to)
    path, _ = FINDER.find_path(start, end, grid)
    return path[1] if len(path) > 1 else None


def normalize(n):
    return int(n / max(abs(n), 1))
