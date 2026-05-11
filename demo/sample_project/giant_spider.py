
from enemy_type import EnemyType


class GiantSpider(EnemyType):
    "a giant spider enemy type"

    def __init__(self):
        super().__init__(enemy_name="giant spider",
                         enemy_hp=80.0,
                         enemy_damage=18.8)
