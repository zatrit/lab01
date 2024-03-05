from typing import Optional
from game import UpdateData
from util import empty_func, foreach


class Effect:
    """Базовый эффект"""

    def __init__(self, image, apply_func=empty_func, update_func=empty_func) -> None:
        self.image = image
        self.apply_func = apply_func
        self.update_func = update_func

    def apply(self, unit):
        self.apply_func(self, unit)

    def get_image(self):
        return self.image

    def update(self, update_data, unit):
        self.update_func(self, update_data, unit)


class Effects:
    """Набор эффектов, реализующий автоматическое применение их для юнитов"""
    effects_list: list[Effect]
    unit: Optional[object]

    def __init__(self) -> None:
        self.effects_list, self.units = [], []
        self.remove_effect = self.effects_list.remove

    def register_unit(self, unit):
        self.unit = unit

    def add_effect(self, effect: Effect):
        self.effects_list.append(effect)
        if self.unit:
            effect.apply(self.unit)

    def update(self, update_data: UpdateData):
        if self.unit:
            foreach(lambda e: e.update(update_data, self.unit), self.effects_list)
