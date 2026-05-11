
from enemy_type import EnemyType
from item import Item
from weapon_type import WeaponType


class Adventurer(object):
    "player character with equipment and inventory"

    def __init__(self, name, equipped_weapon: WeaponType):
        self.name = name
        self.equipped_weapon = equipped_weapon
        self.inventory: list[Item] = []
        self.last_enemy_faced: EnemyType | None = None

    def add_item(self, item: Item):
        self.inventory.append(item)

    def equip_weapon(self, weapon: WeaponType):
        self.equipped_weapon = weapon

    def record_enemy(self, enemy: EnemyType):
        self.last_enemy_faced = enemy
