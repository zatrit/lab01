from dataclasses import field
from effect import Effects
from dataclasses import dataclass


@dataclass
class UnitData:
    """Все свойства юнита, модифицируются через эффекты"""
    effects: Effects = field(default_factory=Effects)
    health: int = 5
    max_health: int = 5
    shield: int = 1
    damage: int = 1
    hit_speed: int = 20
    speed: int = 67
    damage_area: int = 12
    knockback: float = 5.

    def __setattr__(self, __name: str, __value) -> None:
        if __name == "health":
            __value = min(__value, self.max_health)
        super().__setattr__(__name, __value)
