class Client:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.in_range = False

    def set_in_range(self, in_range):
        self.in_range = in_range

    def __str__(self):
        return f"Client at ({self.x}, {self.y}), In Range: {self.in_range}"
