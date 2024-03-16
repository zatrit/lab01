from itertools import cycle
import random
from typing import Iterator
import pygame
from generator import RoguelikeMap
from impl.enemy import Enemy
from impl.level_tiler import CELL_SIZE
from impl.player import Player
from impl.glitch import DISAPEAR_SOUND, glitch
from impl.unit import Unit
from util import LoopedTimer, play_sound
from dataclasses import dataclass
from game import UpdateData
from pathfinding.core.grid import Grid
from pygame.sprite import Group, Sprite


@dataclass
class EnemySpawnProps:
    enemy_group: Group
    overlay_group: Group
    timer_group: Group
    collision_groups: Group
    bushes_group: Group
    player_group: Group
    unit_group: Group
    grid: Grid
    player: Player
    level: RoguelikeMap


class SpeedingUp(Iterator[float]):
    def __init__(self, delay: float) -> None:
        self.delay = delay
        self.multiplier = 1.0

    def __next__(self) -> float:
        self.multiplier *= 0.95
        return max(5, self.delay * self.multiplier)


class EnemySpawner(Sprite):
    """Спрайт для появления врагов по всей карте в случайных местах"""

    def __init__(self, props: EnemySpawnProps, *groups):
        super().__init__(*groups)
        self.props = props
        self.timer = LoopedTimer(SpeedingUp(15), self.glitch)

    def update(self, data: UpdateData):
        self.timer.update(data.elapsed)

    def glitch(self):
        """Создаёт визуальный эффект перед появлением врага"""
        room = random.choice(self.props.level.room_list)
        local_pos = (random.randint(2, n - 2) for n in room[2:])
        room_pos = room[:2]
        pos = tuple(map(CELL_SIZE.__mul__, map(sum, zip(local_pos, room_pos))))

        def on_spawn():
            self.spawn(pos)
            play_sound(DISAPEAR_SOUND, 0.1)

        glitch((*pos, 17, 24), self.props.overlay_group,
               self.props.timer_group, Unit.glitchy_image(), on_spawn)

    def spawn(self, pos):
        # Как много аргументов...
        Enemy(self.props.enemy_group, self.props.unit_group,
              pos=pos, collision_groups=(self.props.collision_groups,),
              bushes_group=self.props.bushes_group,
              overlay_group=self.props.overlay_group,
              player_group=self.props.player_group,
              timer_group=self.props.timer_group,
              player=self.props.player,
              grid=self.props.grid)
