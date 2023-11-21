import math
import random
import threading
import time
import cv2
from particle_Class import global_sol, particle
from router_Class import Router
from visual_Class import Visual


def subtract_coordinates(coord_list1, coord_list2):
    result = [(coord1[0] - coord2[0], coord1[1] - coord2[1]) for coord1, coord2 in zip(coord_list1, coord_list2)]
    return result


def update_particle_position(list_of_position):
    particle_position = [(router.x, router.y) for router in list_of_position]
    particle_position = [(float(coord.x), float(coord.y)) if hasattr(coord, 'x') and hasattr(coord, 'y') else coord for
                         coord in particle_position]
    particle_position = sorted(particle_position, key=lambda coord: (coord[0], coord[1]))
    return particle_position

class PSO:
    def __init__(self, space, routers, clients, second_screen, check_image, radius, combobox_number_particle, sgc_label,
                 fitness_label, height=None, width=None, image_manager=None):
        self.visual = None
        self.social_component = []
        self.cognitive_component = []
        self.combobox_number_particle = combobox_number_particle
        self.sgc_label = sgc_label
        self.fitness_label = fitness_label
        self.radius = radius
        self.swarm = []
        self.particles = None
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

    def PSO_algorithm(self, tk_screen2, max_iterations):
        def iteration_callback(iteration):
            cognitive_weight = 2
            social_weight = 2
            inertia_weight = 0.6

            if self.check_image:
                max_velocity = 50
                self.visual = Visual(tk_screen2, 'PSO', self.check_image)
                self.initialize_swarm_for_image(self.num_particles, 5, self.image_manager.shape_polygon)
            else:
                max_velocity = 10
                self.visual = Visual(tk_screen2, 'PSO', self.check_image)
                self.initialize_swarm_for_rect(self.num_particles, int(self.routers), 5, self.height, self.width)

            self.initialize_velocities(max_velocity)

            for iteration in range(max_iterations):

                self.evaluate_fitness()

                self.update_swarm(inertia_weight, cognitive_weight, social_weight, max_velocity)

                self.update_best_particle()

                self.update_best_global_particle()

                time.sleep(0.4)
                self.visualize_solution(iteration)

                while self.pause_event.is_set():
                    time.sleep(0.1)

            self.output_metrics()  # Implement this func
            while True:
                time.sleep(1000)

        iteration_callback(1)

    def initialize_swarm_for_rect(self, num_particles, num_routers, radius, height, width):
        self.swarm.append([particle() for _ in range(self.num_particles)])
        self.swarm.append([particle() for _ in range(self.num_particles)])
        self.swarm.append(global_sol())
        for i in range(num_particles):
            routers = []
            for _ in range(num_routers):
                y = random.uniform(0, height)
                x = random.uniform(0, width)
                router = Router(x, y, radius)
                routers.append(router)
            self.swarm[0][i].solution = routers
            self.swarm[0][i].position = update_particle_position(self.swarm[0][i].solution)
        self.evaluate_fitness()
        self.update_best_particle()
        self.update_best_global_particle()

    def initialize_swarm_for_image(self, num_particles, radius, shape_polygon):
        self.swarm.append([particle() for _ in range(self.num_particles)])
        self.swarm.append([particle() for _ in range(self.num_particles)])
        self.swarm.append(global_sol())

        for i in range(num_particles):
            routers = []
            while True:
                y = random.uniform(0, 1800)
                x = random.uniform(0, 1800)
                point = (x, y)
                is_inside = cv2.pointPolygonTest(shape_polygon, point, measureDist=False)
                if is_inside == 1:
                    router = Router(x, y, radius)
                    routers.append(router)
                if num_particles == len(routers):
                    self.swarm[0][i].solution = routers
                    self.swarm[0][i].position = update_particle_position(self.swarm[0][i].solution)
                    break
        self.evaluate_fitness()
        self.update_best_particle()
        self.update_best_global_particle()

    def initialize_velocities(self, max_velocity):
        for particle in self.swarm[0]:
            particle.velocity = (random.uniform(-max_velocity, max_velocity),
                                 random.uniform(-max_velocity, max_velocity))

    def calculate_sgc(self, routers):
        visited_clients = set()
        giant_component_size = 0
        for router in routers:
            for client in self.clients:
                if self.visual.check_coverage(router, client, self.radius):
                    visited_clients.add(client)
            giant_component_size = max(giant_component_size, len(visited_clients))
        return giant_component_size

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
            self.visual.mark_covered_clients(particle.solution, self.clients, self.radius)
            counter = 0
            for client in self.clients:
                if client.in_range:
                    counter += 1
            particle.coverage = int((counter / (len(self.clients))) * 100)
            particle.giant_component_size = self.calculate_sgc(particle.solution)

            particle.fitness = 0.7 * particle.giant_component_size + 0.3 * particle.coverage

    def update_swarm(self, inertia_weight, cognitive_weight, social_weight, max_velocity):
        for i in range(len(self.swarm[0])):
            self.cognitive_component.append(cognitive_weight * subtract_coordinates(self.swarm[1][i].position,
                                                                                    self.swarm[0][i].position))
            self.social_component.append(social_weight * subtract_coordinates(self.swarm[2].position,
                                                                              self.swarm[0][i].position))
            for j, router in enumerate(self.swarm[0][i].solution):
                velocity_boost_factor = 1.0 - router.amount_of_coverage
                cognitive_i = self.cognitive_component[i][j]
                social_i = self.social_component[i][j]
                cognitive_x, cognitive_y = cognitive_i
                social_x, social_y = social_i

                router.velocity = [
                    inertia_weight * router.velocity[0] + random.uniform(0, 1) * cognitive_weight * (
                                cognitive_x - router.x) + random.uniform(0, 1) * social_weight * (
                                social_x - router.x),
                    inertia_weight * router.velocity[1] + random.uniform(0, 1) * cognitive_weight * (
                                cognitive_y - router.y) + random.uniform(0, 1) * social_weight * (
                                social_y - router.y)
                ]

                router.velocity = (max(-max_velocity, min(router.velocity[0], max_velocity)),
                                   max(-max_velocity, min(router.velocity[1], max_velocity)))
                router.x += router.velocity[0]
                router.y += router.velocity[1]

                if router.x > self.height or router.x < 0:
                    router.x = random.uniform(0, self.height)
                if router.y > self.width or router.y < 0:
                    router.y = random.uniform(0, self.width)

                self.swarm[0][i].position[j] = (router.x, router.y)

    def update_best_global_particle(self):
        for i in range(len(self.swarm[1])):
            if self.swarm[2].fitness <= self.swarm[1][i].fitness:
                self.swarm[2] = self.swarm[1][i]

    def update_best_particle(self):
        for i in range(len(self.swarm[1])):
            if self.swarm[1][i].fitness <= self.swarm[0][i].fitness:
                self.swarm[1][i] = self.swarm[0][i]

    def visualize_solution(self, iteration):
        value_of_combobox = self.combobox_number_particle.get()
        self.second_screen.iteration_number.set("Iteration number:       " + str(iteration + 1))
        if value_of_combobox == 'Global':
            coverage_percent = self.swarm[2].coverage
            self.second_screen.coverage_percentage.set("Coverage:                 " + str(coverage_percent) + "%")
            self.second_screen.SGC_text.set("Giant component size:    " + str(self.swarm[2].giant_component_size))
            self.second_screen.fitness_text.set("Fitness score:          " + str(round(self.swarm[2].fitness, 2)))
            self.visual.mark_covered_clients(self.swarm[2].solution, self.clients, self.radius)
            if self.check_image:
                self.visual.update_visualization_for_image(self.swarm[2].solution, self.clients, 5,
                                                           self.image_manager.original_image)
            else:
                self.visual.update_visualization_for_rect_PSO(self.swarm[2].solution, self.clients, 5, self.height,
                                                              self.width)
        else:
            coverage_percent = self.swarm[0][int(value_of_combobox) - 1].coverage
            self.second_screen.coverage_percentage.set("Coverage:                 " + str(coverage_percent) + "%")
            self.second_screen.SGC_text.set("Giant component size:    " +
                                            str(self.swarm[0][int(value_of_combobox) - 1].giant_component_size))
            self.second_screen.fitness_text.set("Fitness score:          " +
                                                str(round(self.swarm[0][int(value_of_combobox) - 1].fitness, 2)))
            self.visual.mark_covered_clients(self.swarm[0][int(value_of_combobox) - 1].solution,
                                             self.clients, self.radius)
            if self.check_image:
                self.visual.update_visualization_for_image(self.swarm[0][int(value_of_combobox) - 1].solution,
                                                           self.clients, 5, self.image_manager.original_image)
            else:
                self.visual.update_visualization_for_rect_PSO(self.swarm[0][int(value_of_combobox) - 1].solution,
                                                              self.clients, 5, self.height, self.width)

    def continue_button(self):
        self.pause_event.clear()

    def pause_button(self):
        self.pause_event.set()

    def output_metrics(self):
        pass


