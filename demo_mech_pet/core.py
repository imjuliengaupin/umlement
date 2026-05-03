class MechPet(object):
    def __init__(self, pet_name):
        self.pet_name = pet_name
        self.energy = 100

    def recharge(self):
        self.energy = 100
