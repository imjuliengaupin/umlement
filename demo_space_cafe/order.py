class DrinkOrder(object):
    def __init__(self, guest_name, drink_name):
        self.guest_name = guest_name
        self.drink_name = drink_name
        self.completed = False

    def complete(self):
        self.completed = True
