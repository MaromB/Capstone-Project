import math
import random
import threading
import time
import copy
from collections import defaultdict
from itertools import combinations
import cv2
import numpy as np
from router_Class import Router
from visual_Class import Visual


class GA:
    def __init__(self, space, second_screen, height=None, width=None, imageManager=None):
        self.new_population = []
        self.current_population = []
        self.visual = None
        self.routers_to_show = None
        self.space = space
        self.clients = self.space.clients
        self.height = height
        self.width = width
        self.second_screen = second_screen
        self.num_of_routers = int(self.second_screen.routers)
        self.radius = self.second_screen.radius
        self.check_image = self.second_screen.check_image
        self.thread = None
        self.imageManager = imageManager
        self.pause_event = threading.Event()
        self.start_time = time.time()
        self.pause_time = 0
        self.graph = None
        self.fitness_for_graph = []

    def GA_algorithm(self, tk_screen2, max_iterations):
        def iteration_callback(iteration):
            for iteration in range(max_iterations):
                if iteration == 0 and self.check_image:
                    self.initialize_population_for_image(200)
                    self.visual = Visual(self.second_screen, tk_screen2, 'GA', self.check_image)
                elif iteration == 0 and not self.check_image:
                    self.height = self.space.height
                    self.width = self.space.width
                    self.initialize_population_for_rect(200)
                    self.visual = Visual(self.second_screen, tk_screen2, 'GA', self.check_image)

                self.new_population = copy.deepcopy(self.current_population)

                fitness_scores, coverage_list, giant_list = self.fitness_function(self.new_population)

                self.select_parents(100, fitness_scores)

                self.router_placement_crossover()

                self.mutate_population(0.1)

                # self.resolve_router_overlap_population(self.new_population)

                mutated_fitness_scores = self.fitness_function(self.new_population)

                # Replace the current population with the mutated population if it's better
                if max(mutated_fitness_scores[0]) > max(fitness_scores):
                    self.current_population = self.new_population
                    self.fitness_scores = mutated_fitness_scores
                else:
                    self.current_population = self.current_population

                fitness_scores, coverage_list, giant_list = self.fitness_function(self.current_population)

                self.routers_to_show, index = self.best_configuration_output(fitness_scores)
                self.fitness_for_graph.append(fitness_scores[index])
                self.second_screen.iteration_number.set("Iteration number:     " + str(iteration + 1))
                self.second_screen.coverage_percentage.set("Coverage:                " +
                                                           str(round(coverage_list[index], 1)) + "%")
                self.second_screen.SGC_text.set("Giant component size:      "
                                                + str(giant_list[index]))
                if fitness_scores[index] < 10:
                    self.second_screen.fitness_text.set("Fitness score:                    "
                                                        + str(round(fitness_scores[index], 1)))
                else:
                    self.second_screen.fitness_text.set("Fitness score:                  "
                                                        + str(round(fitness_scores[index], 1)))
                elapsed_time = time.time() - self.start_time - self.pause_time
                formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                self.second_screen.time_text.set("Time:     " + formatted_time)
                self.visual.mark_covered_clients(self.routers_to_show, self.clients, self.radius)
                if self.check_image:
                    self.visual.update_parameters(self.routers_to_show, self.clients, self.radius, 'GA', 'image',
                                                  self.fitness_for_graph, None, None, self.imageManager.original_image,)
                elif not self.check_image:
                    self.visual.update_parameters(self.routers_to_show, self.clients, self.radius, 'GA', 'rect',
                                                  self.fitness_for_graph, self.height, self.width, None)
                if self.pause_event.is_set():
                    self.pause_start_time = time.time()
                    while self.pause_event.is_set():
                        time.sleep(0.1)
                    self.pause_time += time.time() - self.pause_start_time
            while True:
                time.sleep(1000)

        iteration_callback(1)

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
            if distance <= router1.radius and distance <= router2.radius:
                self.graph[router1].append(router2)
                self.graph[router2].append(router1)

        giant_component_size = 0
        visited_nodes = set()
        for router in routers:
            if router not in visited_nodes:
                component_size = self.dfs(router, visited_nodes)
                giant_component_size = max(giant_component_size, component_size)

        return giant_component_size

    def fitness_function(self, population):
        coverage_list = []
        giant_list = []
        fit_list = []
        for routers in population:
            self.visual.mark_covered_clients(routers, self.clients, self.radius)
            counter = 0
            for client in self.clients:
                if client.in_range:
                    counter += 1
            penalty = len(routers) - len(set((router.x, router.y) for router in routers))
            coverage_list.append(counter / len(self.clients) * 100)
            giant_list.append(self.calculate_sgc(routers))
            fitness = ((0.75 * (self.calculate_sgc(routers) / self.num_of_routers))
                       + 0.25 * (counter / len(self.clients)) - 0.3 * penalty) * 100
            fit_list.append(fitness)

        return fit_list, coverage_list, giant_list

    def initialize_population_for_rect(self, num_solutions):
        for _ in range(num_solutions):
            solution = []
            for _ in range(self.num_of_routers):
                y = random.uniform(0, self.height)
                x = random.uniform(0, self.width)
                router = Router(x, y, self.radius)
                solution.append(router)
            self.current_population.append(solution)

    def initialize_population_for_image(self, num_solutions):
        for _ in range(num_solutions):
            solution = []
            while True:
                x = random.uniform(0, 1800)
                y = random.uniform(0, 1800)
                point = (x, y)
                is_inside = cv2.pointPolygonTest(self.imageManager.shape_polygon, point, measureDist=False)
                if is_inside == 1:
                    router = Router(x, y, self.radius)
                    solution.append(router)
                if len(solution) == self.num_of_routers:
                    break
            self.current_population.append(solution)

    def select_parents(self, num_parents, fitness_scores, tournament_size=10):
        copy_population = copy.deepcopy(self.new_population)
        self.new_population.clear()
        while len(self.new_population) < num_parents:
            tournament_indices = np.random.choice(len(copy_population), tournament_size, replace=False)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            selected_index = tournament_indices[np.argmax(tournament_fitness)]
            if copy_population[selected_index] not in self.new_population:
                self.new_population.append(copy_population[selected_index])

    def router_placement_crossover(self):
        copy_population = copy.deepcopy(self.new_population)
        self.new_population.clear()
        num_iterations = 4 * len(copy_population)

        for _ in range(num_iterations):
            i, j = random.sample(range(len(copy_population)), 2)
            parent1, parent2 = copy_population[i], copy_population[j]

            child = self.uniform_crossover(parent1, parent2)

            self.new_population.append(child)

    def uniform_crossover(self, parent1, parent2):
        child = []
        for gene1, gene2 in zip(parent1, parent2):
            if random.choice([True, False]):  # Randomly select genes from parents
                child.append(gene1)
            else:
                child.append(gene2)
        return child

    def mutate_population(self, mutation_rate):
        for routers in self.new_population:
            new_x, new_y = 1, 1
            changed = []
            for i, router in enumerate(routers):
                is_inside = -1
                if random.random() < mutation_rate:
                    if not self.check_image:
                        new_x = random.uniform(0, self.width)
                        new_y = random.uniform(0, self.height)
                        changed.append(i)
                    while self.check_image and is_inside == -1:
                        new_x = random.uniform(0, 1800)
                        new_y = random.uniform(0, 1800)
                        point = (new_x, new_y)
                        is_inside = cv2.pointPolygonTest(self.imageManager.shape_polygon, point, measureDist=False)
                    router.x = new_x
                    router.y = new_y

    def best_configuration_output(self, fitness_scores):
        index = 0
        for i in range(len(self.current_population)):
            if fitness_scores[index] <= fitness_scores[i]:
                index = i
        best_conf = self.current_population[index]
        return best_conf, index

    def calculate_coverage(self, router_x, router_y, client_locations):
        coverage_count = 0
        for client_x, client_y in client_locations:
            distance = ((router_x - client_x) ** 2 + (router_y - client_y) ** 2) ** 0.5
            if distance <= self.radius:
                coverage_count += 1
        return coverage_count

    def continue_button(self):
        self.pause_event.clear()

    def pause_button(self):
        self.pause_event.set()

    def resolve_router_overlap_population(self, population):
        copy_population = copy.deepcopy(population)
        population.clear()
        for routers in copy_population:
            routers_without_overlap = self.resolve_router_overlap_solution(routers)
            population.append(routers_without_overlap)

    def resolve_router_overlap_solution(self, routers):
        resolved_routers = [routers[0]]
        for router in routers[1:]:
            while self.check_overlap_for_one_router(router, resolved_routers):
                new_x, new_y = self.find_new_coordinates()
                router = Router(new_x, new_y, self.radius)
            resolved_routers.append(router)
        return resolved_routers

    def find_new_coordinates(self):
        new_x, new_y = 1, 1
        is_inside = -1.0
        if not self.check_image:
            new_x = random.uniform(0, self.width)
            new_y = random.uniform(0, self.height)
        while self.check_image and is_inside == -1.0:
            new_x = random.uniform(0, 1800)
            new_y = random.uniform(0, 1800)
            point = (new_x, new_y)
            is_inside = cv2.pointPolygonTest(self.imageManager.shape_polygon, point, measureDist=False)
        return new_x, new_y

    def check_overlap_for_one_router(self, router1, routers):
        for router2 in routers:
            if self.distance_between_routers(router1, router2):
                return True
        return False

    def distance_between_routers(self, router1, router2):
        distance = abs(math.sqrt(((router1.x - router2.x) ** 2) + ((router1.y - router2.y) ** 2)))
        return distance < 2 * self.radius
