from enum import Enum
from functools import lru_cache
import random
from assets import load_animation
import pygame
from impl.glitch import GlitchyDeath
from animation import AnimatedSprite
from impl.effects import *


def bat_boost():
    effects = [attack_speed_boost, sharp_bat, damage_boost, knockback_boost]
    return random.choice(effects)()


def char_boost():
    effects = [speed_boost, shield_boost, healing]
    return random.choice(effects)()


class TerminalType(Enum):
    """Тип терминала, всего два типа"""
    BAT = "bat", bat_boost
    CHAR = "char", char_boost


class UpgradeTerminal(GlitchyDeath, AnimatedSprite):
    """Спрайт для терминала прокачки игрока или биты"""
    player_nearby: bool = False

    @property
    @lru_cache(2)
    def real_rect(self):
        return pygame.Rect(self.rect)

    def __init__(self, _type: TerminalType, pos, overlay_group, *groups, timer_group):
        self.default_tag, self.func = _type.value
        super().__init__(load_animation("upgrade-term"),
                         self.default_tag, (*pos, 16, 24), *groups)  # type: ignore
        self.overlay_group = overlay_group
        self.timer_group = timer_group

    def update(self, data) -> None:
        super().update(data)
        # Проверяет, рядом ли игрок, и если да, то использует
        # отдельную анимацию
        self.set_tag(self.default_tag +
                     ("_nearby" if self.player_nearby else ""))

    def glitchy_image(self):
        return self.image

    def interact(self, player):
        if player.mod_points >= 1:
            # Добавляет случайный эффект игроку
            player.mod_points -= 1
            player.unit_data.effects.add_effect(self.func())
