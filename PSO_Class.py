import math
import random
import threading
import copy
import time
from collections import defaultdict
from itertools import combinations
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


def bonus_calculation(routers, radius=5):
    bonus = 0
    checked_pairs = set()  # To store checked pairs to avoid duplication

    for i in range(len(routers)):
        for j in range(i + 1, len(routers)):  # Avoid checking pairs twice
            pair = (i, j) if i < j else (j, i)  # Sort the pair to avoid duplicates
            if pair in checked_pairs:
                continue

            router1 = routers[i]
            router2 = routers[j]

            distance = math.sqrt((router1.x - router2.x) ** 2 + (router1.y - router2.y) ** 2)
            if distance < radius:
                inverse_distance_squared = distance
                bonus += inverse_distance_squared

            checked_pairs.add(pair)

    return bonus


class PSO:
    def __init__(self, space, second_screen, height=None, width=None, image_manager=None):
        self.visual = None
        self.social_component = []
        self.cognitive_component = []
        self.swarm = []
        self.particles = None
        self.space = space
        self.clients = self.space.clients
        self.height = height
        self.width = width
        self.second_screen = second_screen
        self.routers = int(self.second_screen.routers)
        self.radius = self.second_screen.radius
        self.check_image = self.second_screen.check_image
        self.thread = None
        self.num_particles = 20
        self.image_manager = image_manager
        self.pause_event = threading.Event()
        self.start_time = time.time()
        self.pause_time = 0
        self.graph = None
        self.fitness_for_graph = []

    def PSO_algorithm(self, tk_screen2, max_iterations):
        def iteration_callback(iteration):
            cognitive_weight = 2
            social_weight = 2
            inertia_weight = 0.6

            if self.check_image:
                max_velocity = 50
                self.visual = Visual(self.second_screen, tk_screen2, 'PSO', self.check_image)
                self.initialize_swarm_for_image()
            else:
                max_velocity = 10
                self.visual = Visual(self.second_screen, tk_screen2, 'PSO', self.check_image)
                self.initialize_swarm_for_rect()

            self.initialize_velocities(max_velocity)

            for iteration in range(max_iterations):

                self.update_swarm(inertia_weight, cognitive_weight, social_weight, max_velocity)

                self.evaluate_fitness()

                self.update_best_particle()

                self.update_best_global_particle()

                time.sleep(0.4)
                self.visualize_solution(iteration)

                if self.pause_event.is_set():
                    self.pause_start_time = time.time()
                    while self.pause_event.is_set():
                        time.sleep(0.1)
                    self.pause_time += time.time() - self.pause_start_time

            while True:
                time.sleep(1000)

        iteration_callback(1)

    def initialize_swarm_for_rect(self):
        self.swarm.append([particle() for _ in range(self.num_particles)])
        self.swarm.append([particle() for _ in range(self.num_particles)])
        self.swarm.append(global_sol())
        for i in range(self.num_particles):
            routers = []
            for _ in range(int(self.routers)):
                y = random.uniform(0, self.height)
                x = random.uniform(0, self.width)
                router = Router(x, y, self.radius)
                routers.append(router)
            self.swarm[0][i].solution = routers
            self.swarm[0][i].position = update_particle_position(self.swarm[0][i].solution)
        self.update_best_particle()
        self.update_best_global_particle()

    def initialize_swarm_for_image(self):
        self.swarm.append([particle() for _ in range(self.num_particles)])
        self.swarm.append([particle() for _ in range(self.num_particles)])
        self.swarm.append(global_sol())

        for i in range(self.num_particles):
            routers = []
            while True:
                y = random.uniform(0, 1800)
                x = random.uniform(0, 1800)
                point = (x, y)
                is_inside = cv2.pointPolygonTest(self.image_manager.shape_polygon, point, measureDist=False)
                if is_inside == 1:
                    router = Router(x, y, self.radius)
                    routers.append(router)
                if int(self.routers) == len(routers):
                    self.swarm[0][i].solution = routers
                    self.swarm[0][i].position = update_particle_position(self.swarm[0][i].solution)
                    break
        self.update_best_particle()
        self.update_best_global_particle()

    def initialize_velocities(self, max_velocity):
        for particle in self.swarm[0]:
            particle.velocity = (random.uniform(-max_velocity, max_velocity),
                                 random.uniform(-max_velocity, max_velocity))

    def dfs(self, node, visited):
        size = 1
        visited.add(node)
        for neighbor in self.graph[node]:
            if neighbor not in visited:
                size += self.dfs(neighbor, visited)
        return size

    def calculate_sgc(self, routers):
        self.graph = defaultdict(list)
        for router1, router2 in combinations(routers, 2):
            distance = ((router1.x - router2.x) ** 2 + (router1.y - router2.y) ** 2) ** 0.5
            if distance <= router1.radius:
                self.graph[router1].append(router2)
                self.graph[router2].append(router1)

        giant_component_size = 0
        visited_nodes = set()
        for router in routers:
            component_size = self.dfs(router, visited_nodes)
            giant_component_size = max(giant_component_size, component_size)

        return giant_component_size

    def evaluate_fitness(self):
        for particle in self.swarm[0]:
            for router in particle.solution:
                counter = 0
                for client in self.clients:
                    if self.visual.check_coverage(router, client, self.radius):
                        counter += 1
                router.amount_of_coverage = counter
            particle.solution.sort(key=lambda r: r.amount_of_coverage, reverse=True)
            self.visual.mark_covered_clients(particle.solution, self.clients, self.radius)
            counter = 0
            for client in self.clients:
                if client.in_range:
                    counter += 1
            # penalty = len(particle.solution) - len(set((router.x, router.y) for router in particle.solution))
            bonus = bonus_calculation(particle.solution)

            particle.coverage = int((counter / (len(self.clients))) * 100)
            particle.giant_component_size = self.calculate_sgc(particle.solution)

            particle.fitness = ((0.5 * (particle.giant_component_size / len(particle.solution)))
                                + 0.4 * (particle.coverage / 100) + 0.1 * (bonus / (5 * len(particle.solution)))) * 100

    def update_swarm(self, inertia_weight, cognitive_weight, social_weight, max_velocity):
        global x, y
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
                if self.check_image:
                    point = (router.x, router.y)
                    while cv2.pointPolygonTest(self.image_manager.shape_polygon, point, measureDist=False) <= 0:
                        router.y = random.uniform(0, 1800)
                        router.x = random.uniform(0, 1800)
                        point = (router.x, router.y)
                else:
                    if router.x > self.width or router.x < 0:
                        router.x = random.uniform(0, self.width)
                    if router.y > self.height or router.y < 0:
                        router.y = random.uniform(0, self.height)
                self.swarm[0][i].position[j] = (router.x, router.y)

    def update_best_global_particle(self):
        for i in range(len(self.swarm[1])):
            if self.swarm[2].fitness <= self.swarm[1][i].fitness:
                self.swarm[2] = copy.deepcopy(self.swarm[1][i])
        self.fitness_for_graph.append(self.swarm[2].fitness)

    def update_best_particle(self):
        for i in range(len(self.swarm[1])):
            if self.swarm[1][i].fitness <= self.swarm[0][i].fitness:
                self.swarm[1][i] = copy.deepcopy(self.swarm[0][i])

    def visualize_solution(self, iteration):
        self.second_screen.iteration_number.set("Iteration number:       " + str(iteration + 1))
        value_of_combobox = self.second_screen.number_of_particle.get()
        elapsed_time = time.time() - self.start_time - self.pause_time
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        self.second_screen.time_text.set("Time:     " + formatted_time)
        coverage_percent = self.swarm[2].coverage
        self.second_screen.coverage_percentage.set("Coverage:                 " +
                                                   str(round(coverage_percent, 1)) + "%")
        self.second_screen.SGC_text.set("Giant component size:      "
                                        + str(self.swarm[2].giant_component_size))
        if self.swarm[2].fitness < 10:
            self.second_screen.fitness_text.set("Fitness score:                    "
                                                + str(round(self.swarm[2].fitness, 1)))
        else:
            self.second_screen.fitness_text.set("Fitness score:                  "
                                                + str(round(self.swarm[2].fitness, 1)))
        self.visual.mark_covered_clients(self.swarm[2].solution, self.clients, self.radius)
        if self.check_image:
            self.visual.update_parameters(self.swarm[2].solution, self.clients, 5, 'PSO', 'global image',
                                          self.fitness_for_graph, None, None, self.image_manager.original_image)
        else:
            self.visual.update_parameters(self.swarm[2].solution, self.clients, 5, 'PSO', 'global',
                                          self.fitness_for_graph, self.height, self.width, None)
        if value_of_combobox != 'Graph':
            self.visual.mark_covered_clients(self.swarm[0][int(value_of_combobox) - 1].solution,
                                             self.clients, self.radius)
            if self.check_image:
                self.visual.update_parameters(self.swarm[0][int(value_of_combobox) - 1].solution, self.clients, 5, 'PSO'
                                              , 'Particles image', None, None, None, self.image_manager.original_image)
            else:
                self.visual.update_parameters(self.swarm[0][int(value_of_combobox) - 1].solution, self.clients, 5, 'PSO'
                                              , 'Particles', None, self.height, self.width, None)
        else:
            self.visual.update_parameters(self.fitness_for_graph, self.clients, 5, 'PSO', 'graph', None, self.height,
                                          self.width, None)

    def continue_button(self):
        self.pause_event.clear()

    def pause_button(self):
        self.pause_event.set()
