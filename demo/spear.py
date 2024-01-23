
from weapon_type import WeaponType


class Spear(WeaponType):
    "a spear weapon type"

    def __init__(self):
        super().__init__(weapon_name="spear",
                         weapon_damage=15.4,
                         weapon_value=500,
                         weapon_description="a pointy wooden spear")
