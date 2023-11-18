class particle:
    def __init__(self):
        self.solution = []
        self.position = []
        self.velocity = 0
        self.vector = []
        self.coverage = 0
        self.fitness = 0
        self.giant_component_size = 0

    def __str__(self):
        return (f" The position of the Particle is: {self.position}, Velocity: {self.velocity} and the direction:"
                f" {self.vector})")


class global_sol:
    def __init__(self):
        self.solution = []
        self.position = []
        self.velocity = 0
        self.vector = []
        self.coverage = 0
        self.fitness = 0
        self.giant_component_size = 0

    def __str__(self):
        return (f" The position of the Particle is: {self.position}, Velocity: {self.velocity} and the direction:"
                f" {self.vector})")
