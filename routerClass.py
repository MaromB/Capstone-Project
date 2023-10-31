class Router:
    def __init__(self, x, y, radius):
        self.x = x  # X-coordinate of router location
        self.y = y  # Y-coordinate of router location
        self.radius = radius  # Radius of router coverage area

    def __str__(self):
        return f"Router at ({self.x}, {self.y}), Radius: {self.radius}"
