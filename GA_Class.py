import math
import random
import threading
import time
import copy
import cv2
import numpy as np
from routerClass import Router
from visualClass import Visual


def is_better(new_fitness_scores, old_fitness_scores):
    new_total_coverage = sum(new_fitness_scores)  # Calculate the total coverage of the new population
    old_total_coverage = sum(old_fitness_scores)
    return new_total_coverage > old_total_coverage


class GA:
    def __init__(self, space, num_of_routers, clients, second_screen, check_image, radius, height=None, width=None,
                 imageManager=None):
        self.new_population = []
        self.current_population = []
        self.visual = None
        self.space = space
        self.num_of_routers = num_of_routers
        self.routers_to_show = None
        self.clients = clients
        self.radius = radius
        self.height = height
        self.width = width
        self.second_screen = second_screen
        self.check_image = check_image
        self.thread = None
        self.imageManager = imageManager
        self.pause_event = threading.Event()

    def GA_algorithm(self, tk_screen2, max_iterations):
        def iteration_callback(iteration):
            for iteration in range(max_iterations):
                if iteration == 0 and self.check_image:
                    self.initialize_population_for_image(200, self.num_of_routers, self.imageManager.shape_polygon)
                    self.visual = Visual(tk_screen2)
                elif iteration == 0 and not self.check_image:
                    self.height = self.space.height
                    self.width = self.space.width
                    self.initialize_population(200, self.num_of_routers)
                    self.visual = Visual(tk_screen2)

                self.new_population = copy.deepcopy(self.current_population)

                fitness_scores = self.fitness_function(self.new_population)

                self.select_parents(100, fitness_scores)

                self.router_placement_crossover()

                self.mutate_population(0.05)

                self.resolve_router_overlap_population(self.new_population)

                self.current_population = self.new_population

                self.routers_to_show, coverage_percentage = self.best_configuration_output(fitness_scores)
                self.second_screen.iteration_number.set("Iteration number:       " + str(iteration + 1))
                self.second_screen.coverage_percentage.set("Coverage:            " + str(coverage_percentage) + "%")
                self.visual.mark_covered_clients(self.routers_to_show, self.clients, self.radius, 'GA')
                if self.check_image:
                    self.visual.update_visualization_for_image(self.routers_to_show, self.clients, self.radius,
                                                               self.imageManager.original_image)
                elif not self.check_image:
                    self.visual.update_visualization_for_rectangle(self.routers_to_show, self.clients, self.radius,
                                                                   self.height, self.width)
                while self.pause_event.is_set():
                    time.sleep(0.1)
            while True:
                time.sleep(1000)
                
        iteration_callback(1)

    def fitness_function(self, population):
        total_coverage = []
        for routers in population:
            counter = 0
            for router in routers:
                for client in self.clients:
                    if self.visual.check_coverage(router, client, self.radius, 'GA'):
                        counter += 1
            total_coverage.append(counter / len(self.clients) * 100)
        return total_coverage

    def initialize_population(self, num_solutions, num_of_routers):
        for _ in range(num_solutions):
            solution = []
            for _ in range(num_of_routers):
                y = random.uniform(0, self.height)
                x = random.uniform(0, self.width)
                router = Router(x, y, self.radius)
                solution.append(router)
            self.current_population.append(solution)
        self.resolve_router_overlap_population(self.current_population)

    def initialize_population_for_image(self, num_solutions, num_of_routers, shape_polygon):
        for _ in range(num_solutions):
            solution = []
            while True:
                x = random.uniform(0, 1800)
                y = random.uniform(0, 1800)
                point = (x, y)
                is_inside = cv2.pointPolygonTest(shape_polygon, point, measureDist=False)
                if is_inside == 1:
                    router = Router(x, y, self.radius)
                    solution.append(router)
                if len(solution) == num_of_routers:
                    break
            self.current_population.append(solution)
        self.resolve_router_overlap_population(self.current_population)

    def mutate_population(self, mutation_rate):
        for routers in self.new_population:
            self.mutate_solution(routers, mutation_rate)

    def mutate_solution(self, routers, mutation_rate):
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

    def calculate_coverage(self, router_x, router_y, client_locations):
        coverage_count = 0
        for client_x, client_y in client_locations:
            distance = ((router_x - client_x) ** 2 + (router_y - client_y) ** 2) ** 0.5
            if distance <= self.radius:
                coverage_count += 1
        return coverage_count
    
    def best_configuration_output(self, fitness_scores):
        index = 0
        coverage_percentage = 0
        for i in range(len(self.current_population)):
            if fitness_scores[index] <= fitness_scores[i]:
                index = i
                coverage_percentage = fitness_scores[i]
        best_conf = self.current_population[index]
        return best_conf, int(coverage_percentage)

    def select_parents(self, num_parents, fitness_scores, tournament_size=4):
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
        cur_list = []
        for _ in range(4):
            for i in range(0, len(copy_population), 2):
                parent1 = copy_population[i]
                parent2 = copy_population[i + 1]

                # Randomly choose one of the parents as the base placement
                base_parent = parent1 if random.random() < 0.5 else parent2

                # Probability of inheriting each router position (adjust as needed)
                inherit_probability = 0.5
                routers_from_base = 0
                # Iterate through router positions in the base parent
                for router_position in base_parent:
                    # Decide whether to inherit this router position
                    if random.random() < inherit_probability:
                        cur_list.append(router_position)
                        routers_from_base += 1

                routers_to_inherit = len(base_parent) - routers_from_base

                if routers_to_inherit > 0:
                    other_parent = parent2 if base_parent == parent1 else parent1
                    routers_to_inherit = min(routers_to_inherit, len(other_parent))
                    routers_inherited = random.sample(other_parent, routers_to_inherit)
                    cur_list.extend(routers_inherited)

                if len(cur_list) == routers_to_inherit + routers_from_base:
                    self.new_population.append(cur_list)
                    cur_list = []

    def continue_button(self):
        self.pause_event.clear()

    def pause_button(self):
        self.pause_event.set()
