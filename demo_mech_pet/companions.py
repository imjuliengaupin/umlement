from attachments import LaserWhiskers, RocketTail
from core import MechPet


class SpaceCat(MechPet):
    def __init__(self):
        self.tail = RocketTail()
        self.whiskers = LaserWhiskers()
        super().__init__("space cat")


class MoonCorgi(MechPet):
    def __init__(self):
        self.tail = RocketTail()
        super().__init__("moon corgi")
