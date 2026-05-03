class CafeMenu(object):
    def __init__(self):
        self.drinks = ["nebula latte", "comet espresso", "saturn chai"]

    def has_drink(self, drink_name):
        return drink_name in self.drinks
