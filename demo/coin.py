
from item import Item


class Coin(Item):
    "base class for all game currency"

    def __init__(self, coin_color, coin_value):
        self.coin_color = coin_color
        self.coin_value = coin_value

        super().__init__(item_name=f"{self.coin_color} coin",
                         item_value=self.coin_value,
                         item_description=f"a round {self.coin_color} coin with a {str(self.coin_value)} stamped on the front")

    def get_coin_color(self):
        return self.coin_color

    def get_coin_value(self):
        return self.coin_value

    def set_coin_color(self, coin_color):
        self.coin_color = coin_color

    def set_coin_value(self, coin_value):
        self.coin_value = coin_value
