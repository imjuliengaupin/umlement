
from item import Item


class WeaponType(Item):
    "base class for all player weapons"

    def __init__(self, weapon_name, weapon_damage, weapon_value, weapon_description):
        self.weapon_damage = weapon_damage

        super().__init__(item_name=weapon_name,
                         item_value=weapon_value,
                         item_description=weapon_description)

    def __str__(self):
        return f"\nweapon name: {super().get_item_name()}\nweapon damage: {str(self.weapon_damage)}\nweapon value: {str(super().get_item_value())}\nweapon description: {super().get_item_description()}\n"

    def get_weapon_damage(self):
        return self.weapon_damage

    def set_weapon_damage(self, weapon_damage):
        self.weapon_damage = weapon_damage
