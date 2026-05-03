from barista_bot import BaristaBot
from menu import CafeMenu


class OrbitLounge(object):
    def __init__(self):
        self.menu = CafeMenu()
        self.barista = BaristaBot("Dock-7", self.menu)
