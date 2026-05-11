
class Item(object):
    "base class for all game items"

    def __init__(self, item_name, item_value, item_description):
        self.item_name = item_name
        self.item_value = item_value
        self.item_description = item_description

    def __str__(self):
        return f"\nitem name: {self.item_name}\nitem value: {str(self.item_value)}\nitem description: {self.item_description}\n"

    def get_item_name(self):
        return self.item_name

    def get_item_value(self):
        return self.item_value

    def get_item_description(self):
        return self.item_description

    def set_item_name(self, item_name):
        self.item_name = item_name

    def set_item_value(self, item_value):
        self.item_value = item_value

    def set_item_description(self, item_description):
        self.item_description = item_description
