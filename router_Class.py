class Router:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.amount_of_coverage = 0
        self.velocity = 0
        self.vector = (0, 0)

    def __str__(self):
        return f"Router at ({self.x}, {self.y}), Radius: {self.radius}, Amount of clients coverage: " \
               f"{self.amount_of_coverage}"
