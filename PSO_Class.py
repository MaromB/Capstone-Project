import math
import random
import threading
import time
import cv2
from routerClass import Router
from visualClass import Visual
import numpy as np


class PSO:
    def __init__(self, space, routers, clients, second_screen, check_image, height=None, width=None,
                 image_manager=None):
        self.swarm = None
        self.particles = None
        self.visual = None
        self.space = space
        self.routers = routers
        self.clients = clients
        self.height = height
        self.width = width
        self.second_screen = second_screen
        self.check_image = check_image
        self.thread = None
        self.num_particles = 20
        self.image_manager = image_manager
        self.pause_event = threading.Event()
        self.global_best = []
        self.global_best = []
        self.global_best.solution = []
        self.global_best.coverage = 0
        self.best = []
        for i in range(self.num_particles):
            self.best[i].coverage = 0
            self.best[i].solutions = []

    def PSO_algorithm(self, tk_screen2, max_iterations):
        def iteration_callback(iteration):
            max_velocity = 5
            cognitive_weight = 1.5  # exploration
            social_weight = 1.5  # exploitation
            inertia_weight = 0.7

            if self.check_image:
                self.swarm = self.initialize_swarm_for_image(self.num_particles, int(self.routers), 5,
                                                             self.image_manager.shape_polygon)
            else:
                self.swarm = self.initialize_swarm_for_rect(self.num_particles, int(self.routers), self.height,
                                                            self.width)

            # Initialize particle velocities only once at the beginning
            for particle in self.swarm:
                velocity_values = self.initialize_particle_velocity(len(self.particles), max_velocity)
                particle.velocity = velocity_values

            for iteration in range(max_iterations):
                self.update_particles(inertia_weight, cognitive_weight, social_weight, max_velocity)
                # 5. Evaluate Fitness
                self.evaluate_fitness()  # Implement this function

                # 6. Update Global Best
                for particle in self.swarm:
                    if particle.coverage < self.global_best.coverage:
                        self.global_best.solution = self.particles.solution
                        self.global_best.coverage = self.particles.coverage

                # 7. Visualize Best Solution
                self.visualize_solution(self.global_best.solution)  # Implement this function

                # 8. Termination Condition (Optional)
                if self.termination_condition(iteration):
                    break

                time.sleep(0.4)

                # 9. Visualize Final Result
                self.visualize_solution(self.global_best.solution)  # Implement this function

                # 10. Output Metrics (Optional)
                self.output_metrics(self.global_best.solution)  # Implement this function

        iteration_callback(1)

    def update_particles(self, inertia_weight, cognitive_weight, social_weight, max_velocity):
        for particle, i in self.swarm:
            self.global_best.solution = self.find_global_best_solution()  # need to implement this function

            cognitive_component = [cognitive_weight * (self.best[i].coverage - particle.coverage)
                                   for _ in range(len(particle))]  # quality of solution==coverage

            social_component = [social_weight * (self.global_best.coverage - particle.coverage)
                                for _ in range(len(particle))]

            particle.velocity = inertia_weight * particle.velocity + cognitive_component + social_component

            if particle.velocity > max_velocity:
                particle.velocity = max_velocity
            elif particle.velocity < -max_velocity:
                particle.velocity = -max_velocity

            particle.solution = self.update_router_locations(particle.solution, particle.velocity)
            # need to implement this function

    def initialize_particle_velocity(self, routers, max_velocity):
        velocity_of_routers = [random.uniform(-max_velocity, max_velocity) for _ in range(routers)]
        return velocity_of_routers

    def initialize_swarm_for_rect(self, num_particles, routers, radius, height, width):
        self.swarm = []
        self.particles = []
        for _ in range(num_particles):
            self.particles.coverage = 0
            self.particles.solution = []
            self.particles.velocity = random.uniform(-5, 5)
            self.routers.clear()
            for _ in range(routers):
                y = random.randint(0, height)
                x = random.randint(0, width)
                router = Router(x, y, radius)
                self.routers.append(router)
            self.particles.append(self.routers)
        self.swarm.append(self.particles)
        self.fitness_function(self.swarm, self.clients, 5)
        return self.swarm

    def initialize_swarm_for_image(self, num_particles, routers, radius, shape_polygon):
        self.swarm = []
        self.particles = []
        for _ in range(num_particles):
            self.particles.coverage = 0
            self.particles.solution = []
            self.particles.velocity = random.uniform(-5, 5)
            self.routers.clear()
            while True:
                y = random.randint(0, 1800)
                x = random.randint(0, 1800)
                point = (x, y)
                is_inside = cv2.pointPolygonTest(shape_polygon, point, measureDist=False)
                if is_inside == 1:
                    router = Router(x, y, radius)
                    self.routers.append(router)
                if len(self.particles) == routers:
                    self.particles.append(self.routers)
                    break
        self.swarm.append(self.particles)
        self.fitness_function(self.swarm, self.clients, 5)
        return self.swarm

    def fitness_function(self, client_locations, radius):

        for particle, j in self.swarm:
            for router, i in particle:
                counter = 0
                for client in client_locations:
                    if self.isItCovered(router, client, radius):
                        counter += 1
            particle.sort(key=lambda r: router.amount_of_coverage, reverse=True)

        for particle in self.swarm:
            total_coverage = sum(router.amount_of_coverage for router in particle)
            particle.coverage = (total_coverage / (len(client_locations) * len(particle)) * 100)


    def isItCovered(self, router, client, radius):
        distance = abs(math.sqrt(((router[0] - client.x) ** 2) + ((router[1] - client.y) ** 2)))
        return distance <= radius

    def find_global_best_solution(self):
        pass

    def update_router_locations(self, solution, velocity):
        pass

    def continue_button(self):
        self.pause_event.clear()

    def pause_button(self):
        self.pause_event.set()

    def termination_condition(self, iteration):
        pass

    def visualize_solution(self, solution):
        pass

    def output_metrics(self, global_best_solution):
        pass


