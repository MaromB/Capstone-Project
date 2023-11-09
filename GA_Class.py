import math
import random
import threading
import time
import cv2

from routerClass import Router
from visualClass import Visual
import numpy as np


def select_parents(population, fitness_scores, num_parents, tournament_size=1):
    selected_parents = []
    while len(selected_parents) < num_parents:
        tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        selected_index = tournament_indices[np.argmax(tournament_fitness)]

        if population[selected_index] not in selected_parents:
            selected_parents.append(population[selected_index])
    return selected_parents


def router_placement_crossover(selected_parents):
    new_population = []
    cur_list = []
    for _ in range(4):
        for i in range(0, len(selected_parents), 2):
            parent1 = selected_parents[i]
            parent2 = selected_parents[i + 1]

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
                new_population.append(cur_list)
                cur_list = []
    return new_population


def is_better(new_fitness_scores, old_fitness_scores):
    new_total_coverage = sum(new_fitness_scores)  # Calculate the total coverage of the new population
    old_total_coverage = sum(old_fitness_scores)
    return new_total_coverage > old_total_coverage


def best_configuration_output(current_population, fitness_scores):
    index = 0
    coverage_percentage = 0
    for i in range(len(current_population)):
        if fitness_scores[index] <= fitness_scores[i]:
            index = i
            coverage_percentage = fitness_scores[i]
    best_conf = current_population[index]
    return best_conf, int(coverage_percentage)


class GA:
    def __init__(self, space, num_of_routers, clients, second_screen, check_image, radius, height=None, width=None,
                 imageManager=None):
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
                    self.current_population = self.initialize_population_for_image(4, self.num_of_routers,
                                                                                   self.imageManager.shape_polygon)
                    self.visual = Visual(tk_screen2)
                elif iteration == 0 and not self.check_image:
                    self.height = self.space.height
                    self.width = self.space.width
                    self.current_population = self.initialize_population(4, self.num_of_routers)
                    self.visual = Visual(tk_screen2)
                # Evaluate the fitness of each solution in the population
                fitness_scores = self.fitness_function(self.current_population, self.clients)
                # Select parents for crossover (you can use various selection methods)
                descendants = select_parents(self.current_population, fitness_scores, int(len(fitness_scores) / 2))
                # Create a new population using crossover
                new_population = router_placement_crossover(descendants)
                # Apply mutation to some solutions in the new population
                if self.check_image:
                    mutated_population = self.mutate_population(new_population, 0.2, self.imageManager.shape_polygon)
                    resolved_routers = self.resolve_router_overlap_population(mutated_population)
                else:
                    mutated_population = self.mutate_population(new_population, 0.2, None)
                    resolved_routers = self.resolve_router_overlap_population(mutated_population)
                # Evaluate the fitness of the mutated population
                mutated_fitness_scores = self.fitness_function(resolved_routers, self.clients)
                # Replace the current population with the mutated population if it's better
                #if is_better(mutated_fitness_scores, fitness_scores): ## check this!!!!!1111
                self.current_population = resolved_routers
                fitness_scores = mutated_fitness_scores
                # Visualize the best current state of the routers
                self.routers_to_show, coverage_percentage = best_configuration_output(self.current_population, fitness_scores)

                self.second_screen.iteration_number.set("Iteration number:       " + str(iteration + 1))
                self.second_screen.coverage_percentage.set("Coverage:            " + str(coverage_percentage) + "%")
                self.visual.mark_covered_clients(self.routers_to_show, self.clients, self.radius, 'GA')
                if self.check_image:
                    self.visual.update_visualization_for_image(self.routers_to_show, self.clients, self.radius,
                                                               self.imageManager.original_image)
                elif not self.check_image:
                    self.visual.update_visualization_for_rectangle(self.routers_to_show, self.clients, self.radius, self.height,
                                                                   self.width)
                while self.pause_event.is_set():
                    time.sleep(0.1)
            while True:
                time.sleep(1000)

            # return self.current_population

        iteration_callback(1)

    def fitness_function(self, current_population, client_locations):
        total_coverage = []
        for routers in current_population:
            counter = 0
            for router in routers:
                for client in client_locations:
                    if self.visual.check_coverage(router, client, self.radius, 'GA'):
                        counter += 1
            total_coverage.append(counter / len(client_locations) * 100)
        return total_coverage

    def initialize_population(self, num_solutions, routers):
        population = []
        for _ in range(num_solutions):
            solution = []
            for _ in range(routers):
                y = random.uniform(0, self.height)
                x = random.uniform(0, self.width)
                router = Router(x, y, self.radius)
                solution.append(router)
            population.append(solution)
        return population

    def initialize_population_for_image(self, num_solutions, routers, shape_polygon):
        population = []
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
                if len(solution) == routers:
                    break
            population.append(solution)
        return population

    def mutate_solution(self, solution, mutation_rate, shape_polygon):
        new_x, new_y = 1, 1
        mutated_solution = []
        for router in solution:
            is_inside = -1
            if random.random() < mutation_rate:
                if not self.check_image:
                    new_y = random.uniform(0, self.height)
                    new_x = random.uniform(0, self.width)
                while self.check_image and is_inside == -1:
                    new_y = random.uniform(0, 1800)
                    new_x = random.uniform(0, 1800)
                    point = (new_x, new_y)
                    is_inside = cv2.pointPolygonTest(shape_polygon, point, measureDist=False)
                router.x = new_x
                router.y = new_y
            mutated_solution.append(router)
        return mutated_solution

    def mutate_population(self, population, mutation_rate, shape_polygon1=None):
        shape_polygon = shape_polygon1
        mutated_population = []
        for solution in population:
            mutated_solution = self.mutate_solution(solution, mutation_rate, shape_polygon)
            mutated_population.append(mutated_solution)
        return mutated_population

    def resolve_router_overlap_population(self, population):
        routers_population = []
        for routers in population:
            routers_without_overlap = self.resolve_router_overlap_solution(routers)
            routers_population.append(routers_without_overlap)
        return routers_population

    def resolve_router_overlap_solution(self, routers):
        resolved_routers = [routers[0]]
        for router in routers[1:]:
            while self.check_overlap_for_one_router(router, resolved_routers):
                router = self.find_new_coordinates()
            resolved_routers.append(router)

        return resolved_routers

    def find_new_coordinates(self):
        new_x, new_y = 1, 1
        is_inside = -1.0
        if not self.check_image:
            new_x = random.uniform(0, self.width)
            new_y = random.uniform(0, self.height)
        while self.check_image and is_inside == -1.0:
            new_y = random.uniform(0, 1800)
            new_x = random.uniform(0, 1800)
            point = (new_x, new_y)
            is_inside = cv2.pointPolygonTest(self.imageManager.shape_polygon, point, measureDist=False)
        new_router = Router(new_x, new_y, self.radius)
        return new_router

    def check_overlap_for_one_router(self, router1, routers):
        for router2 in routers:
            if self.distance_between_routers(router1, router2):
                return True
        return False

    def distance_between_routers(self, router1, router2):
        distance = abs(math.sqrt(((router1.x - router2.x) ** 2) + ((router1.y - router2.y) ** 2)))
        return distance <= 2 * self.radius

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
