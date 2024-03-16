from abc import abstractmethod
from functools import lru_cache
from math import atan2, cos, sin
from typing import Iterable, Union

import pygame
from animation import PriorityAnimatedSprite

from assets import load_animation, load_sound
from game import UpdateData
from impl.glitch import GlitchyDeath
from impl.level_tiler import CELL_SIZE
from impl.unit_data import UnitData
from sprites import Hitbox, SpriteTimer

from util import empty_func, play_sound

# Обратный квадратный корень из двух. Нужен для оптимизации
SQRT2 = 2 ** 0.5
# Картинка, которая рисуется поверх сущности, когда она в кустах
BUSHES_OVERLAY = pygame.image.load(
    "assets/sprite/player-bushes-overlay.png").convert_alpha()

HIT_SOUND = load_sound("assets/sound/hit.mp3")
WAVING_SOUND = load_sound("assets/sound/waving.mp3")


@lru_cache(16)
def create_hitbox(topleft, rect, offset=(0, 0)):
    return Hitbox(pygame.Rect(*map(sum, zip(offset, rect[:2], topleft)), *rect[2:]))


class Unit(GlitchyDeath, PriorityAnimatedSprite):
    """Спрайт абстрактного персонажа"""

    unit_data: UnitData
    """Данные о персонаже"""

    moving: bool = False
    """Двигается ли персонаж"""

    hitbox: tuple[int, int, int, int] = 3, 17, 11, 9
    """Хитбокс для проверки столкновения со стенами"""

    attack_hitbox: tuple[int, int, int, int] = 0, 0, 17, 17
    """Хитбокс, определяющий площадь атаки"""

    collision_groups: list[pygame.sprite.Group]
    """Группа, с которой персонаж будет сталкиваться"""

    bushes_group: pygame.sprite.Group
    """Группа, в которой персонаж скрывается за кустами"""

    velocity: Iterable[Union[int, float]]
    """Дополнительная скорость, зависящая от удара"""

    p_brighten: float = 0
    """Предыдущее значение яркости осветления"""

    brighten: float = 0
    """Яркость осветления"""

    @property
    def hitting(self):
        """Свойство, возвращающие True, если сейчас проигрывается анимация удара"""
        return self.tag == "hit1"

    @property
    def collides_bush(self):
        hitbox = self.create_hitbox((1, 11, 15, 18))
        return pygame.sprite.spritecollideany(hitbox, self.bushes_group)

    def __init__(self, *groups, pos: tuple[int, int], collision_groups, bushes_group, overlay_group, hittable_group, timer_group, sprite="player") -> None:
        super().__init__(load_animation(sprite), "idle", (*pos, 11, 24), *groups)
        self.tag_priority("idle", 0)
        self.tag_priority("walk", 0)
        self.tag_priority("swap_side", 1)
        self.tag_priority("hit1", 2)

        self.moving = False
        self.unit_data = UnitData()
        self.unit_data.effects.register_unit(self)
        self.overlay_group = overlay_group
        self.collision_groups = collision_groups
        self.bushes_group = bushes_group
        self.hittable_group = hittable_group
        self.timer_group = timer_group
        self.velocity = 0, 0
        self.hit_timer = None
        self.hit_somebody = empty_func

    def move_directions(self, speed, horizontal, vertical):
        if horizontal and vertical:
            return speed * horizontal / SQRT2, speed * vertical / SQRT2
        return speed * horizontal, speed * vertical

    def update(self, data: UpdateData):
        horizontal, vertical = self.get_move_direction(data)

        self.moving = horizontal or vertical  # type: ignore
        swap = (horizontal < 0) != self.render_props.flip_x and horizontal
        super().update(data)
        self.unit_data.effects.update(data)

        self.velocity = tuple(0.85 * a for a in self.velocity)
        self.brighten = sum(map(abs, self.velocity))
        self.move(*self.velocity)

        if self.p_brighten != self.brighten:
            self.force_redraw = True
            self.p_brighten = self.brighten

        if self.moving:
            speed = self.unit_data.hit_speed \
                if self.hitting else self.unit_data.speed
            direction = self.move_directions(speed, horizontal, vertical)
            self.moving = self.move(*map(data.elapsed.__mul__, direction))

        self.update_move_tag(False)
        if swap:
            self.set_tag("swap_side")
        if horizontal:
            self.render_props.flip_x = horizontal < 0

        if self.unit_data.health <= 0:
            self.kill()

    def create_hitbox(self, rect, offset=(0, 0)):
        return create_hitbox(self.rect[:2], rect, offset)  # type: ignore

    def on_hit(self, by):
        c1, c2 = map(reversed, map(
            tuple, (self.get_center(), by.get_center())))
        angle = atan2(*(b - a for a, b in zip(c2, c1)))
        self.velocity = map(sum, zip(self.velocity,
                                     map(by.unit_data.knockback.__mul__,
                                         (cos(angle), sin(angle)))))

        self.unit_data.health -= by.unit_data.damage / self.unit_data.shield

        play_sound(HIT_SOUND)

    def hit(self):
        """Функция, вызываемая для удара, создаёт таймер по истечению которого
        наносится удар"""
        def hit_timer_end():
            """Функция, отвечающая за удар"""
            hitbox = self.create_hitbox(self.attack_hitbox)
            for s in self.hittable_group:
                s: Unit
                if pygame.sprite.collide_rect(hitbox, s):  # type: ignore
                    self.hit_somebody(s)
                    s.on_hit(self)
            play_sound(WAVING_SOUND, .5)

        if self.set_tag("hit1"):
            self.hit_timer = SpriteTimer(0.40, hit_timer_end, self.timer_group)

    def move(self, mx, my):
        # Оригинальный прямог., используемый для
        # оценки движения при возврате значения
        ogrect = self.rect
        x, y, *size = self.rect

        def group_check(g):
            return pygame.sprite.spritecollideany(hitbox, g)

        # Создаётся копия прямогуг., и вычисляется следующее
        # расположение при движении
        hitbox = self.create_hitbox(self.hitbox, offset=(mx, 0))
        if not any(map(group_check, self.collision_groups)):
            x += mx
        hitbox = self.create_hitbox(self.hitbox, offset=(0, my))
        if not any(map(group_check, self.collision_groups)):
            y += my
        self.rect = x, y, *size  # type: ignore
        return (x, y) != ogrect[0:2]

    def update_move_tag(self, force):
        # Если проигрывается анимация ходьбы, если сущность идёт
        self.set_tag("walk" if self.moving else "idle", force=force)

    @abstractmethod
    def get_move_direction(self, data: UpdateData) -> tuple[int, int]:
        """Абстрактная функция для управления игрока или ИИ бота"""
        ...

    def animation_finished(self, _):
        self.update_move_tag(True)

    def overlay(self, image: pygame.Surface):
        # Осветляет персонажа, чтобы улучшить ощущение атак игроком
        brighten = min(int(32 * self.brighten), 255)
        image.fill((brighten, brighten, brighten, 0),
                        special_flags=pygame.BLEND_RGBA_ADD)

        # Скрывает часть спрайта, чтобы показать объёмность кустов
        if self.collides_bush:
            size = width, _ = image.get_size()
            image = image.subsurface((0, 0, width, 15))
            image2 = pygame.Surface(size)
            image2.set_colorkey("black")
            image2.blit(image, (0, 0))
            image2.blit(BUSHES_OVERLAY, (4, 15))
            return image2

        return image

    def get_center(self) -> Iterable[int]:
        """Возвращает центр хитбокса персонажа"""
        hitbox_center = (c + a + b // 2 for a,
                         b, c in zip(self.hitbox[:2], self.hitbox[2:], self.rect[:2]))
        return hitbox_center

    def get_cell(self) -> tuple[int, int]:
        """Возвращает клетку персонажа на поле"""
        return tuple(int(n / CELL_SIZE) for n in self.get_center())  # type: ignore

    def kill_hit_timer(self):
        if self.hit_timer:
            self.hit_timer.kill()

    def kill(self) -> None:
        self.kill_hit_timer()
        super().kill()

    @staticmethod
    def glitchy_image():
        return pygame.image.load("assets/sprite/dummy.png")
