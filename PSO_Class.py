import math
import random
import threading
import time
import cv2
from routerClass import Router
from visualClass import Visual


def calculate_direction(router, inertia_weight, cognitive_component, height, width):
    new_x_direction = inertia_weight * router.vector[0] + cognitive_component * router.speed
    new_y_direction = inertia_weight * router.vector[1] + cognitive_component * router.speed
    new_x = router.x + new_x_direction
    new_y = router.y + new_y_direction
    new_x = min(max(0, new_x), width)
    new_y = min(max(0, new_y), height)
    router.vector = (new_x_direction, new_y_direction)
    router.x = new_x
    router.y = new_y


class my_global:
    def __init__(self):
        self.coverage = 0
        self.solution = []


class particle_list:
    def __init__(self):
        self.coverage = 0
        self.solution = []


class PSO:
    def __init__(self, space, routers, clients, second_screen, check_image, radius, height=None, width=None,
                 image_manager=None):
        self.radius = radius
        self.swarm = None
        self.particles = None
        self.visual = None
        self.space = space
        self.routers = routers
        self.clients = clients
        self.height = int(height)
        self.width = int(width)
        self.second_screen = second_screen
        self.check_image = check_image
        self.thread = None
        self.num_particles = 20
        self.image_manager = image_manager
        self.pause_event = threading.Event()
        self.global_best = my_global()
        self.best = [particle_list() for _ in range(self.num_particles)]

    def PSO_algorithm(self, tk_screen2, max_iterations):
        def iteration_callback(iteration):
            max_velocity = 5
            cognitive_weight = 1.5  # exploration
            social_weight = 1.5  # exploitation
            inertia_weight = 0.7

            if self.check_image:
                self.initialize_swarm_for_image(self.num_particles, 5, self.image_manager.shape_polygon)
                self.visual = Visual(tk_screen2)
            else:
                self.initialize_swarm_for_rect(self.num_particles, int(self.routers), 5, self.height, self.width)
                self.visual = Visual(tk_screen2)

            self.initialize_velocities(max_velocity)

            for iteration in range(max_iterations):
                self.update_swarm(inertia_weight, cognitive_weight, social_weight, max_velocity)

                self.evaluate_fitness()

                time.sleep(0.4)
                self.update_best_particle()
                self.update_best_global_particle()
                self.visualize_solution()
                while self.pause_event.is_set():
                    time.sleep(0.1)

                self.output_metrics()  # Implement this function

        iteration_callback(1)

    def visualize_solution(self):
        self.visual.mark_covered_clients(self.global_best, self.clients, self.radius, 'PSO')
        self.visual.update_visualization_for_rectangle(self.global_best, self.clients, 5, self.height, self.width)

    def evaluate_fitness(self):
        for particle in self.swarm:
            for router in particle.solution:
                counter = 0
                for client in self.clients:
                    if self.visual.check_coverage(router, client, self.radius, 'PSO'):
                        counter += 1
                router.amount_of_coverage = counter
            particle.solution.sort(key=lambda r: router.amount_of_coverage, reverse=True)

        for particle in self.swarm:
            total_coverage = sum(router.amount_of_coverage for router in particle.solution)
            particle.coverage = (total_coverage / (len(self.clients) * len(particle.solution)) * 100)

    def update_swarm(self, inertia_weight, cognitive_weight, social_weight, max_velocity):
        for i, particle in enumerate(self.swarm):

            cognitive_component = [cognitive_weight * (self.best[i].coverage - self.particles[i].coverage)
                                   for _ in range(self.num_particles)]  # quality of solution==coverage

            social_component = [social_weight * (self.global_best.coverage - self.particles[i].coverage)
                                for _ in range(self.num_particles)]

            for router in particle.solution:
                self.evaluate_fitness()
                speed_boost_factor = 1.0 - router.amount_of_coverage
                router.speed = inertia_weight * router.speed + ((cognitive_component[i] + social_component[i]) *
                                                                speed_boost_factor)
                if router.speed > max_velocity:
                    router.speed = max_velocity
                elif router.speed < -max_velocity:
                    router.speed = -max_velocity

                calculate_direction(router, inertia_weight, cognitive_component[i], self.height, self.width)

    def initialize_velocities(self, max_velocity):
        for particle in self.swarm:
            for router in particle.solution:
                router.speed = random.uniform(-max_velocity, max_velocity)
                angle = random.uniform(0, 2 * math.pi)
                router.vector = (math.cos(angle), math.sin(angle))

    def initialize_swarm_for_rect(self, num_particles, num_routers, radius, height, width):
        self.particles = [particle_list() for _ in range(self.num_particles)]
        for i in range(num_particles):
            routers = []
            for _ in range(num_routers):
                y = random.randint(0, height)
                x = random.randint(0, width)
                router = Router(x, y, radius)
                routers.append(router)
            self.particles[i].solution = routers
        self.swarm = self.particles

    def initialize_swarm_for_image(self, num_particles, radius, shape_polygon):
        self.particles = [particle_list() for _ in range(self.num_particles)]
        for i in range(num_particles):
            routers = []
            while True:
                y = random.randint(0, 1800)
                x = random.randint(0, 1800)
                point = (x, y)
                is_inside = cv2.pointPolygonTest(shape_polygon, point, measureDist=False)
                if is_inside == 1:
                    router = Router(x, y, radius)
                    self.routers.append(router)
                if len(self.particles) == len(routers):
                    self.particles[i].solution = routers
                    break
        self.swarm.append(self.particles)

    def update_best_global_particle(self):
        for particle in self.swarm:
            if self.global_best.coverage < particle.coverage:
                self.global_best.coverage = particle.coverage
                self.global_best.solution = particle.solution

    def update_best_particle(self):
        for i, particle in enumerate(self.swarm):
            if self.best[i].coverage < particle.coverage:
                self.best[i].coverage = particle.coverage
                self.best[i].solution = particle.solution

    def find_global_best_solution(self):
        pass

    def update_routers_locations(self, current_solution, velocities):
        updated_solution = []

        for router, velocity in zip(current_solution, velocities):
            x, y = router.x, router.y
            new_x = x + velocity * router.vector[0]  # Update the x-coordinate
            new_y = y + velocity * router.vector[1]  # Update the y-coordinate

            # Ensure the router stays within bounds (if needed)
            # Add boundary conditions if routers should stay within certain limits

            updated_router = Router(new_x, new_y, router.radius)
            updated_solution.append(updated_router)

        return updated_solution

    def continue_button(self):
        self.pause_event.clear()

    def pause_button(self):
        self.pause_event.set()

    def output_metrics(self):
        pass
