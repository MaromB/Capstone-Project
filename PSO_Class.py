import math
import random
import threading
import time
import cv2
from particle_Class import global_sol, particle
from routerClass import Router
from visualClass import Visual


def subtract_coordinates(coord_list1, coord_list2):
    result = [(coord1[0] - coord2[0], coord1[1] - coord2[1]) for coord1, coord2 in zip(coord_list1, coord_list2)]
    return result


def update_particle_position(list_of_position):
    particle_position = [(router.x, router.y) for router in list_of_position]
    particle_position = [(int(coord.x), int(coord.y)) if hasattr(coord, 'x') and hasattr(coord, 'y') else coord for
                         coord in particle_position]
    particle_position = sorted(particle_position, key=lambda coord: (coord[0], coord[1]))
    return particle_position


class PSO:
    def __init__(self, space, routers, clients, second_screen, check_image, radius, combobox_number_particle,
                 height=None, width=None, image_manager=None):
        self.social_component = []
        self.cognitive_component = []
        self.combobox_number_particle = combobox_number_particle
        self.radius = radius
        self.swarm = []
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
        self.global_best = global_sol()
        self.best = [particle() for _ in range(self.num_particles)]

    def PSO_algorithm(self, tk_screen2, max_iterations):
        def iteration_callback(iteration):
            max_velocity = 5
            cognitive_weight = 2
            social_weight = 2
            inertia_weight = 0.6

            if self.check_image:
                self.initialize_swarm_for_image(self.num_particles, 5, self.image_manager.shape_polygon)
                self.visual = Visual(tk_screen2, 'PSO')
            else:
                self.initialize_swarm_for_rect(self.num_particles, int(self.routers), 5, self.height, self.width)
                self.visual = Visual(tk_screen2, 'PSO')

            self.initialize_velocities(max_velocity)

            for iteration in range(max_iterations):

                self.update_swarm(inertia_weight, cognitive_weight, social_weight, max_velocity)

                self.evaluate_fitness()

                self.update_best_particle()

                self.update_best_global_particle()

                time.sleep(0.4)
                self.visualize_solution(iteration)

                while self.pause_event.is_set():
                    time.sleep(0.1)

            self.output_metrics()  # Implement this function
            while True:
                time.sleep(1000)

        iteration_callback(1)

    def visualize_solution(self, iteration):
        coverage_percent = self.global_best.coverage
        self.second_screen.iteration_number.set("Iteration number:       " + str(iteration + 1))
        self.second_screen.coverage_percentage.set("Coverage:                 " + str(coverage_percent) + "%")
        if self.combobox_number_particle == 'Global':
            self.visual.mark_covered_clients(self.swarm[2].solution, self.clients, self.radius)
            self.visual.update_visualization_for_rect_PSO(self.swarm[2].solution, self.clients, 5, self.height,
                                                          self.width, self.combobox_number_particle)

        else:
            self.visual.mark_covered_clients(self.swarm[0][int(self.combobox_number_particle) - 1].solution,
                                             self.clients, self.radius)
            self.visual.update_visualization_for_rect_PSO(self.swarm[0][int(self.combobox_number_particle) - 1],
                                                          self.clients, 5, self.height, self.width,
                                                          self.combobox_number_particle)

    def evaluate_fitness(self):
        for particle in self.swarm[0]:
            for router in particle.solution:
                counter = 0
                for client in self.clients:
                    if self.visual.check_coverage(router, client, self.radius):
                        counter += 1
                router.amount_of_coverage = counter
            particle.solution.sort(key=lambda r: router.amount_of_coverage, reverse=True)

        for particle in self.swarm[0]:
            total_coverage = sum(router.amount_of_coverage for router in particle.solution)
            particle.coverage = int((total_coverage / (len(self.clients))) * 100)

    def update_swarm(self, inertia_weight, cognitive_weight, social_weight, max_velocity):
        for i in range(len(self.swarm[0])):
            self.cognitive_component.append(cognitive_weight * subtract_coordinates(self.swarm[1][i].position,
                                                                                    self.swarm[0][i].position))
            self.social_component.append(social_weight * subtract_coordinates(self.swarm[2].position,
                                                                              self.swarm[0][i].position))

            for j, router in enumerate(self.swarm[0][i].solution):
                self.evaluate_fitness()
                speed_boost_factor = 1.0 - router.amount_of_coverage

                cognitive_i = self.cognitive_component[i][j]
                social_i = self.social_component[i][j]
                cognitive_x, cognitive_y = cognitive_i
                social_x, social_y = social_i

                router.vector = [inertia_weight * router.vector[0] + (
                        cognitive_weight * cognitive_x + social_weight * social_x) * speed_boost_factor,
                                 inertia_weight * router.vector[1] + (
                                         cognitive_weight * cognitive_y + social_weight * social_y) * speed_boost_factor
                                 ]

                if router.vector[0] > max_velocity:
                    router.vector[0] = max_velocity
                elif router.vector[0] < -max_velocity:
                    router.vector[0] = -max_velocity

                if router.vector[1] > max_velocity:
                    router.vector[1] = max_velocity
                elif router.vector[1] < -max_velocity:
                    router.vector[1] = -max_velocity

                router.x += router.vector[0]
                router.y += router.vector[1]

    def initialize_velocities(self, max_velocity):
        for particle in self.swarm[0]:
            for router in particle.solution:
                router.speed = random.uniform(-max_velocity, max_velocity)
                angle = random.uniform(0, 2 * math.pi)
                router.vector = (math.cos(angle), math.sin(angle))

    def initialize_swarm_for_rect(self, num_particles, num_routers, radius, height, width):
        self.swarm.append([particle() for _ in range(self.num_particles)])
        global_best = global_sol()
        best = [particle() for _ in range(self.num_particles)]
        self.swarm.append(best)
        self.swarm.append(global_best)
        for i in range(num_particles):
            routers = []
            for _ in range(num_routers):
                y = random.randint(0, height)
                x = random.randint(0, width)
                router = Router(x, y, radius)
                routers.append(router)
            self.swarm[0][i].solution = routers
            self.swarm[0][i].position = update_particle_position(self.swarm[0][i].solution)
            self.swarm[1][i].solution = routers
            self.swarm[1][i].position = update_particle_position(self.swarm[1][i].solution)
            self.update_best_global_particle()

    def initialize_swarm_for_image(self, num_particles, radius, shape_polygon):
        self.swarm.append([particle() for _ in range(self.num_particles)])
        global_best = global_sol()
        best = [particle() for _ in range(self.num_particles)]
        self.swarm.append(best)
        self.swarm.append(global_best)
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
                if num_particles == len(routers):
                    self.swarm[0][i].solution = routers
                    self.swarm[0][i].position = update_particle_position(self.swarm[0][i].solution)
                    self.swarm[1][i].solution = routers
                    self.swarm[1][i].position = update_particle_position(self.swarm[1][i].solution)
                    self.update_best_global_particle()

                break

    def update_best_global_particle(self):
        self.global_best.coverage = -1
        for i in range(len(self.swarm[1])):
            if self.swarm[2].coverage < self.swarm[1][i].coverage:
                self.swarm[2].coverage = self.swarm[1][i].coverage
                self.swarm[2].solution = self.swarm[1][i].solution
        self.global_best.position = update_particle_position(self.swarm[2].solution)
        return

    def update_best_particle(self):
        for i in range(len(self.swarm[1])):
            if self.swarm[1][i].coverage < self.swarm[0][i].coverage:
                self.swarm[1][i].coverage = self.swarm[0][i].coverage
                self.swarm[1].solution = self.swarm[0][i].solution

    def update_routers_locations(self, current_solution, velocities):
        updated_solution = []

        for router, velocity in zip(current_solution, velocities):
            x, y = router.x, router.y
            new_x = x + velocity * router.vector[0]
            new_y = y + velocity * router.vector[1]

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
