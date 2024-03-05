import random
from effect import Effect
import pygame
from game import UpdateData


effect_image: pygame.Surface = pygame.image.load(
    "assets/sprite/effects.png")
"""Картинка со всеми эффектами"""
effect_w, effect_h = effect_size = 7, 7
"""Размер кадра эффекта"""
n_effects = int(effect_image.get_width() // effect_w)
"""Колличество картинок для эффектов """
EFFECT_IMAGES = [effect_image.subsurface(
    (effect_w * i, 0, *effect_size)).convert_alpha() for i in range(n_effects)]
"""Список изображений эффектов"""


def speed_boost():
    """Эффект, выдаваемый игроку по-умолчанию, увеличивает скорость на 8"""
    def apply(_, unit):
        unit.unit_data.speed += 8
        unit.unit_data.hit_speed += 4
    return Effect(EFFECT_IMAGES[2], apply_func=apply)


def shield_boost():
    """Эффект, улучшающий броню игрока игрока"""
    def apply(_, unit):
        unit.unit_data.shield += 0.5
        unit.unit_data.speed -= 4
        unit.unit_data.hit_speed -= 2
    return Effect(EFFECT_IMAGES[3], apply_func=apply)


def attack_speed_boost():
    """Эффект, повышающий скорость атаки игрока"""
    def apply(_, unit):
        unit.tag_speed("hit1", unit.tag_speeds.get("hit1", 1) + 0.125)
    return Effect(EFFECT_IMAGES[4], apply_func=apply)


def sharp_bat():
    """Эффект, имеющий шанс наложить кровотечение на врага с шансом 20%, вероятности складываются, если таких эффектов несколько"""
    def blood_chance(s, og):
        if not random.randint(0, 5):
            s.unit_data.effects.add_effect(blooding())
        og(s)

    def apply(_, unit):
        og = unit.hit_somebody
        unit.hit_somebody = lambda s: blood_chance(s, og)
    return Effect(EFFECT_IMAGES[5], apply_func=apply)


def damage_boost():
    """Эффект, повышающий общий урон в ближнем бою"""
    def apply(_, unit):
        unit.unit_data.damage += 0.5
    return Effect(EFFECT_IMAGES[6], apply_func=apply)


def knockback_boost():
    """Эффект, повышающий отдачу от удара"""
    def apply(_, unit):
        unit.unit_data.knockback += 0.75
    return Effect(EFFECT_IMAGES[8], apply_func=apply)


def blooding():
    """Эффект, периодически наносящий 1 единицу урона раз в 2 секунды на протяжении 6 секунд"""

    return temporary_hp_modifier(-1, EFFECT_IMAGES[1], 3, 2)


def healing():
    """Эффект, периодически наносящий 1 единицу урона раз в 2 секунды на протяжении 6 секунд"""
    return temporary_hp_modifier(1, EFFECT_IMAGES[7], 3, 1)


def temporary_hp_modifier(hp, img, n, period):
    """Эффект, действующий n раз с заданным периодом, изменяющий хп игрока"""
    counter = 0
    n_times = 0

    def update(effect, update_data: UpdateData, unit):
        nonlocal counter, n_times
        unit_data = unit.unit_data
        if n_times == n:
            unit_data.effects.remove_effect(effect)
        counter += update_data.elapsed

        if counter // period > 0:
            n_times += 1
            counter %= period
            unit_data.health += hp
    return Effect(img, update_func=update)