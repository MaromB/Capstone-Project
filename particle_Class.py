class particle:
    def __init__(self):
        self.coverage = 0
        self.solution = []
        self.position = []

    def __str__(self):
        return f" The position of the Particle is {self.position})"


class global_sol:
    def __init__(self):
        self.coverage = 0
        self.solution = []
        self.position = []

    def __str__(self):
        return f" The position of the Particle is {self.position})"
