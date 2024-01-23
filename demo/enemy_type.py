
class EnemyType(object):
    "base class for all enemy types"

    def __init__(self, enemy_name, enemy_hp, enemy_damage):
        self.enemy_name = enemy_name
        self.enemy_hp = enemy_hp
        self.enemy_damage = enemy_damage

    def __str__(self):
        return f"\nenemy name: {self.enemy_name}\nenemy hp: {str(self.enemy_hp)}\nenemy damage: {str(self.enemy_damage)}\n"

    def get_enemy_name(self):
        return self.enemy_name

    def get_enemy_hp(self):
        return self.enemy_hp

    def get_enemy_damage(self):
        return self.enemy_damage

    def set_enemy_name(self, enemy_name):
        self.enemy_name = enemy_name

    def set_enemy_hp(self, enemy_hp):
        self.enemy_hp = enemy_hp

    def set_enemy_damage(self, enemy_damage):
        self.enemy_damage = enemy_damage

    def is_enemy_alive(self):
        return self.enemy_hp > 0.0
