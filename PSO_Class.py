import math
import random
import threading
import time
import cv2
from visualClass import Visual
import numpy as np


class GA:
    def __init__(self, space, routers, clients, second_screen, check_image, height=None, width=None, imageManager=None):
        self.image_manager = None
        self.visual = None
        self.space = space
        self.routers = routers
        self.clients = clients
        self.height = height
        self.width = width
        self.second_screen = second_screen
        self.check_image = check_image
        self.thread = None
        self.imageManager = imageManager
        self.pause_event = threading.Event()

    def PSO_algorithm(self, tk_screen2, max_iterations):
        # 1. Initialize PSO Parameters
        num_particles = 20
        max_velocity = 5
        c1 = 2.0  # Cognitive parameter
        c2 = 2.0  # Social parameter

        # 2. Initialize Swarm
        swarm = self.initialize_swarm(num_particles)  # Implement this function

        # Initialize global best solution and fitness
        global_best_solution = None
        global_best_fitness = float('inf')  # Initialize with a high value for minimization

        # 3. Iteration Loop
        for iteration in range(max_iterations):
            # 4. Update Particle Positions and Velocities
            self.update_particles(swarm, max_velocity, c1, c2, global_best_solution)

            # 5. Evaluate Fitness
            self.evaluate_fitness(swarm)  # Implement this function

            # 6. Update Global Best
            for particle in swarm:
                if particle.fitness < global_best_fitness:
                    global_best_solution = particle.solution
                    global_best_fitness = particle.fitness

            # 7. Visualize Best Solution
            self.visualize_solution(global_best_solution)  # Implement this function

            # 8. Termination Condition (Optional)
            if self.termination_condition(iteration):
                break

        # 9. Visualize Final Result
        self.visualize_solution(global_best_solution)  # Implement this function

        # 10. Output Metrics (Optional)
        self.output_metrics(global_best_solution)  # Implement this function

    def initialize_swarm(self, num_solutions, routers, height, width):
        swarm = []
        for _ in range(num_solutions):
            solution = []
            for _ in range(routers):
                y = random.randint(0, height)
                x = random.randint(0, width)
                solution.append((x, y))
            swarm.append(solution)
        return swarm

    def initialize_swarm_for_image(self, num_solutions, routers, shape_polygon):
        swarm = []
        for _ in range(num_solutions):
            solution = []
            while True:
                y = random.randint(0, 1800)
                x = random.randint(0, 1800)
                point = (x, y)
                is_inside = cv2.pointPolygonTest(shape_polygon, point, measureDist=False)
                if is_inside == 1:
                    solution.append((x, y))
                if len(solution) == routers:
                    break
            swarm.append(solution)
        return swarm


    def continue_button(self):
        self.pause_event.clear()

    def pause_button(self):
        self.pause_event.set()