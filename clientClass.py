class Client:
    def __init__(self, x, y):
        self.x = x  # wight
        self.y = y  # height
        self.in_range = False  # Variable to indicate if the client is in router range

    def set_in_range(self, in_range):
        self.in_range = in_range

    def __str__(self):
        return f"Client at ({self.x}, {self.y}), In Range: {self.in_range}"
