import math
import random
import threading
import time
import cv2
from visualClass import Visual
import numpy as np


def update_particles(swarm, best_solutions, inertia_weight, cognitive_weight, social_weight, max_velocity):
    for particle in swarm:
        global_best_solution = find_global_best_solution(swarm)  # need to implement this function

        cognitive_component = [cognitive_weight * (best_solutions[i] - particle.fitness)
                               for i in range(len(particle))]  # quality of solution==coverage

        social_component = [social_weight * (global_best_solution[i] - particle.fitness)
                            for i in range(len(particle))]

        particle.velocity = inertia_weight * particle.velocity + cognitive_component + social_component

        if particle.velocity > max_velocity:
            particle.velocity = max_velocity
        elif particle.velocity < -max_velocity:
            particle.velocity = -max_velocity

        particle.solution = update_router_locations(particle.velocity)  # need to implement this function


def initialize_particle_velocity(routers, max_velocity):
    velocity_of_routers = [random.uniform(-max_velocity, max_velocity) for _ in range(routers)]
    return velocity_of_routers


class PSO:
    def __init__(self, space, routers, clients, second_screen, check_image, height=None, width=None,
                 image_manager=None):
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
        self.image_manager = image_manager
        self.pause_event = threading.Event()

    def PSO_algorithm(self, tk_screen2, max_iterations):
        def iteration_callback(iteration):
            num_particles = 20
            max_velocity = 5
            cognitive_weight = 1.5  # exploration
            social_weight = 1.5  # exploitation
            inertia_weight = 0.7
            global_best_solution = []
            best_solutions = [float('inf')] * 20
            global_best_fitness = float('inf')  # Initialize with a high value for minimization

            if self.check_image:
                swarm = self.initialize_swarm_for_image(num_particles, int(self.routers),
                                                        self.imageManager.shape_polygon)
            else:
                swarm = self.initialize_swarm_for_rect(num_particles, int(self.routers), self.height, self.width)

            # Initialize particle velocities only once at the beginning
            for particle in swarm:
                velocity_values = initialize_particle_velocity(len(particle), max_velocity)
                particle.velocity = velocity_values

            for iteration in range(max_iterations):
                update_particles(swarm, best_solutions, inertia_weight, cognitive_weight, social_weight, max_velocity)
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

                time.sleep(0.4)

                # 9. Visualize Final Result
                self.visualize_solution(global_best_solution)  # Implement this function

                # 10. Output Metrics (Optional)
                self.output_metrics(global_best_solution)  # Implement this function

        iteration_callback(1)

    def initialize_swarm_for_rect(self, num_particles, routers, height, width):
        swarm = []
        particle = []
        for _ in range(num_particles):
            particle.solution = []
            particle.velocity = random.uniform(-5, 5)
            for _ in range(routers):
                y = random.randint(0, height)
                x = random.randint(0, width)
                particle.solution.append((x, y))
            particle.fitness = self.fitness_function(particle.solution, self.clients, 5)
            swarm.append(particle)
        return swarm

    def initialize_swarm_for_image(self, num_particles, routers, shape_polygon):
        swarm = []
        particle = []
        for _ in range(num_particles):
            particle.solution = []
            particle.velocity = random.uniform(-5, 5)
            while True:
                y = random.randint(0, 1800)
                x = random.randint(0, 1800)
                point = (x, y)
                is_inside = cv2.pointPolygonTest(shape_polygon, point, measureDist=False)
                if is_inside == 1:
                    particle.append((x, y))
                if len(particle) == routers:
                    break
            particle.fitness = self.fitness_function(particle.solution, self.clients, 5)
            swarm.append(particle)
        return swarm

    def fitness_function(self, particle, client_locations, radius):
        for router in particle:
            counter = 0
            for client in client_locations:
                if self.isItCovered(router, client, radius):
                    counter += 1
        coverage = (counter / len(client_locations) * 100)
        return coverage

    def isItCovered(self, router, client, radius):
        distance = abs(math.sqrt(((router[0] - client.x) ** 2) + ((router[1] - client.y) ** 2)))
        return distance <= radius

    def continue_button(self):
        self.pause_event.clear()

    def pause_button(self):
        self.pause_event.set()
