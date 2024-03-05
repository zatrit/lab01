import random
import pygame
from generator import RoguelikeMap
from impl.enemy import Enemy
from impl.level_tiler import CELL_SIZE
from impl.player import Player
from impl.glitch import glitch
from impl.unit import Unit
from util import LoopedTimer
from dataclasses import dataclass
from game import UpdateData
from pathfinding.core.grid import Grid


@dataclass
class EnemySpawnProps:
    enemy_group: pygame.sprite.Group
    overlay_group: pygame.sprite.Group
    timer_group: pygame.sprite.Group
    collision_groups: pygame.sprite.Group
    bushes_group: pygame.sprite.Group
    player_group: pygame.sprite.Group
    unit_group: pygame.sprite.Group
    grid: Grid
    player: Player
    level: RoguelikeMap


class EnemySpawner(pygame.sprite.Sprite):
    """Спрайт для появления врагов по всей карте в случайных местах"""

    def __init__(self, props: EnemySpawnProps, *groups):
        super().__init__(*groups)
        self.props = props
        self.timer = LoopedTimer([10, 15], self.glitch)

    def update(self, data: UpdateData):
        self.timer.update(data.elapsed)

    def glitch(self):
        """Создаёт визуальный эффект перед появлением врага"""
        room = random.choice(self.props.level.room_list)
        local_pos = (random.randint(2, n - 2) for n in room[2:])
        room_pos = room[:2]
        pos = tuple(map(CELL_SIZE.__mul__, map(sum, zip(local_pos, room_pos))))

        glitch((*pos, 17, 24), self.props.overlay_group,
               self.props.timer_group, Unit.glitchy_image(), lambda: self.spawn(pos))

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
