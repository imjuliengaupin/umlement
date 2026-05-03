from order import DrinkOrder


class BaristaBot(object):
    def __init__(self, station_name, menu):
        self.station_name = station_name
        self.menu = menu
        self.last_order = None

    def queue_order(self, guest_name, drink_name):
        self.last_order = DrinkOrder(guest_name, drink_name)
        return self.last_order

    def brew(self):
        return self.last_order
