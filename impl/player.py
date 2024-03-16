import pygame
from assets import load_sound

from game import CAMERA_SIZE, UpdateData
from .effect_render import EffectsRender
from impl.effects import speed_boost
from impl.unit import Unit
from sprites import Hitbox
from util import empty_func, play_music, play_sound

NEG_HALF_CAMERA_SIZE = tuple(-n // 2 for n in CAMERA_SIZE)
WALKING_SOUND_ARGS = {"maxtime": 500, "volume": 0.5}

GRASS_SOUND = load_sound("assets/sound/walking_grass.mp3")
CONCRETE_SOUND = load_sound("assets/sound/walking_concrete.mp3")


class Player(Unit):
    # Клавиши управления игроком
    keys: pygame.key.ScancodeWrapper
    # Хитбокс для взаимодействия с окружающими объектами
    interaction_hitbox = (2, -10, 13, 15)

    def __init__(self, *groups, pos: tuple[int, int], collision_groups, bushes_group,
                 overlay_group, enemy_group, timer_group, interaction_group, sprite="player") -> None:
        super().__init__(*groups, pos=pos, collision_groups=collision_groups,
                         bushes_group=bushes_group, overlay_group=overlay_group,
                         sprite=sprite, timer_group=timer_group, hittable_group=enemy_group)
        self.effects = EffectsRender(
            self.unit_data.effects, self, overlay_group)
        self.unit_data.effects.add_effect(speed_boost())
        self.enemy_group = enemy_group
        self.interaction_group = interaction_group
        self.mod_points_listener = empty_func
        self.mod_points: int = 0

    def get_move_direction(self, _: UpdateData) -> tuple[int, int]:
        keys = self.keys = pygame.key.get_pressed()
        horizontal = (keys[pygame.K_d] | keys[pygame.K_RIGHT]) - \
                     (keys[pygame.K_a] | keys[pygame.K_LEFT])
        vertical = (keys[pygame.K_s] | keys[pygame.K_DOWN]) - \
                   (keys[pygame.K_w] | keys[pygame.K_UP])
        return horizontal, vertical

    def update(self, data: UpdateData):
        super().update(data)

        # Проигрывает звук ходьбы каждые 30 кадров
        if self.moving and data.update_number % 30 == 0:
            sound = GRASS_SOUND if self.collides_bush else CONCRETE_SOUND
            play_sound(sound, **WALKING_SOUND_ARGS)

        in_hitbox = self.create_hitbox(self.interaction_hitbox)
        for spr in self.interaction_group:
            spr.player_nearby = pygame.sprite.collide_rect(
                Hitbox(spr.real_rect), in_hitbox)

        if self.keys[pygame.K_SPACE]:
            self.hit()

        if self.keys[pygame.K_e]:
            self.interact()

        vision_hitbox = self.create_hitbox(
            (0, 0, *CAMERA_SIZE), NEG_HALF_CAMERA_SIZE)

        for enemy in self.enemy_group:
            enemy.see_player = pygame.sprite.collide_rect(vision_hitbox, enemy)

    def interact(self):
        in_hitbox = self.create_hitbox(self.interaction_hitbox)
        for spr in self.interaction_group:
            if pygame.sprite.collide_rect(
                    Hitbox(spr.real_rect), in_hitbox):
                spr.interact(self)
                return

    def __setattr__(self, __name: str, __value):
        if __name == "mod_points":
            self.mod_points_listener(__value)
        return super().__setattr__(__name, __value)

    def kill(self) -> None:
        play_music("assets/sound/game_back_sound.mp3",
                   fade_ms=2500, volume=0.5)
        self.effects.kill()
        return super().kill()
