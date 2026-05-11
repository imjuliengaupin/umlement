
from weapon_type import WeaponType


class Sword(WeaponType):
    "a sword weapon type"

    def __init__(self):
        super().__init__(weapon_name="sword",
                         weapon_damage=20.2,
                         weapon_value=1000,
                         weapon_description="a sharp steel sword")
