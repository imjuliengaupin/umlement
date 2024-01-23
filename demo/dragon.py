
from enemy_type import EnemyType


class Dragon(EnemyType):
    "a dragon enemy type"

    def __init__(self):
        super().__init__(enemy_name="dragon",
                         enemy_hp=100.0,
                         enemy_damage=26.2)
