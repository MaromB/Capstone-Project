import math
import random
import threading
import time
import cv2
from visualClass import Visual
import numpy as np


def initialize_population(num_solutions, routers, height, width):
    population = []
    for _ in range(num_solutions):
        solution = []
        for _ in range(routers):
            y = random.randint(0, height)
            x = random.randint(0, width)
            solution.append((x, y))
        population.append(solution)
    return population


def initialize_population_for_image(num_solutions, routers, shape_polygon):
    population = []
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
        population.append(solution)
    return population


def select_parents(population, fitness_scores, num_parents, tournament_size=5):
    selected_parents = []
    while len(selected_parents) < num_parents:
        # Perform tournament selection
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


def calculate_coverage(router_x, router_y, client_locations, radius):
    coverage_count = 0
    for client_x, client_y in client_locations:
        distance = ((router_x - client_x) ** 2 + (router_y - client_y) ** 2) ** 0.5
        if distance <= radius:
            coverage_count += 1
    return coverage_count


def best_configuration_output(current_population, fitness_scores):
    best_conf = []
    index = 0
    coverage_percentage = 0
    for i in range(len(current_population)):
        if fitness_scores[index] <= fitness_scores[i]:
            index = i
            coverage_percentage = fitness_scores[i]
    best_conf = current_population[index]
    return best_conf, int(coverage_percentage)


def distanceBetweenRouters(router1, router2, radius):
    distance = abs(math.sqrt(((router1[0] - router2[0]) ** 2) + ((router1[1] - router2[1]) ** 2)))
    return distance <= 2 * radius


def checkOverlapForOneRouter(router1, routers, radius):
    for router2 in routers:
        if distanceBetweenRouters(router1, router2, radius):
            return True
    return False


class Algorithm:
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

    def ga_algorithm(self, tk_screen2, max_iterations):
        def iteration_callback(iteration):
            for iteration in range(max_iterations):
                if iteration == 0 and self.check_image:
                    self.current_population = initialize_population_for_image(20, int(self.routers),
                                                                              self.imageManager.shape_polygon)

                elif iteration == 0 and not self.check_image:
                    self.current_population = initialize_population(20, int(self.routers), self.space.height,
                                                                    self.space.width)
                # Evaluate the fitness of each solution in the population
                fitness_scores = self.fitness_function(self.current_population, self.clients, 5)
                # Select parents for crossover (you can use various selection methods)
                descendants = select_parents(self.current_population, fitness_scores, int(len(fitness_scores) / 2))
                # Create a new population using crossover
                new_population = router_placement_crossover(descendants)
                # Apply mutation to some solutions in the new population
                if self.check_image:
                    mutated_population = self.mutate_population(new_population, 0.2, None, None,
                                                                self.imageManager.shape_polygon)
                    resolved_routers = self.resolve_router_overlap_population(mutated_population, 5, None, None,
                                                                              self.imageManager.shape_polygon)
                else:
                    mutated_population = self.mutate_population(new_population, 0.2, self.height, self.width, None)
                    resolved_routers = self.resolve_router_overlap_population(mutated_population, 5, self.height,
                                                                              self.width, None)
                # Evaluate the fitness of the mutated population
                mutated_fitness_scores = self.fitness_function(resolved_routers, self.clients, 5)
                # Replace the current population with the mutated population if it's better
                if is_better(mutated_fitness_scores, fitness_scores):
                    self.current_population = resolved_routers
                    fitness_scores = mutated_fitness_scores
                # Visualize the best current state of the routers
                self.routers, coverage_percentage = best_configuration_output(self.current_population, fitness_scores)
                if not self.visual:
                    self.visual = Visual(tk_screen2)
                self.second_screen.iteration_number.set("Iteration number:       " + str(iteration + 1))
                self.second_screen.coverage_percentage.set("Coverage:            " + str(coverage_percentage) + "%")
                self.visual.mark_covered_clients(self.routers, self.clients, 5)
                if self.check_image:
                    self.visual.update_visualization_for_image(self.routers, self.clients, 5,
                                                               self.imageManager.original_image)
                elif not self.check_image:
                    self.visual.update_visualization_for_rectangle(self.routers, self.clients, 5, self.height,
                                                                   self.width)
                while self.pause_event.is_set():
                    time.sleep(0.1)
            while True:
                time.sleep(1000)

            # print("done")
            # return self.current_population

        iteration_callback(1)

    def fitness_function(self, current_population, client_locations, radius):
        total_coverage = []
        for routers in current_population:
            counter = 0
            for router in routers:
                for client in client_locations:
                    if self.isItCovered(router, client, radius):
                        counter += 1
            total_coverage.append(counter / len(client_locations) * 100)
        return total_coverage

    def mutate_solution(self, solution, mutation_rate, height, width, shape_polygon):
        new_x, new_y = 1, 1
        mutated_solution = []
        for router_x, router_y in solution:
            is_inside = -1
            if random.random() < mutation_rate:
                if not self.check_image:
                    new_y = random.uniform(0, int(height))
                    new_x = random.uniform(0, int(width))
                while self.check_image and is_inside == -1:
                    new_y = random.uniform(0, 1800)
                    new_x = random.uniform(0, 1800)
                    point = (new_x, new_y)
                    is_inside = cv2.pointPolygonTest(shape_polygon, point, measureDist=False)
            else:
                new_x = router_x
                new_y = router_y
            # Add the mutated router to the new list
            mutated_solution.append((int(new_x), int(new_y)))
        return mutated_solution

    def mutate_population(self, population, mutation_rate, height1=None, width1=None, shape_polygon1=None):
        height = height1
        width = width1
        shape_polygon = shape_polygon1
        mutated_population = []
        for solution in population:
            mutated_solution = self.mutate_solution(solution, mutation_rate, height, width, shape_polygon)
            mutated_population.append(mutated_solution)
        return mutated_population

    def resolve_router_overlap_solution(self, routers, radius, height, width, shape_polygon):
        resolved_routers = [routers[0]]
        new_router = ()
        for router in routers[1:]:
            overlapping = False
            if checkOverlapForOneRouter(router, resolved_routers, radius):
                new_router = self.findNewCoordinates(height, width, shape_polygon)
                overlapping = True
            if overlapping:
                while checkOverlapForOneRouter(new_router, resolved_routers, radius):
                    new_router = self.findNewCoordinates(height, width, shape_polygon)
                resolved_routers.append(new_router)
            else:
                resolved_routers.append(router)
        return resolved_routers

    def resolve_router_overlap_population(self, population, radius, height1=None, width1=None, shape_polygon1=None):
        height = height1
        width = width1
        shape_polygon = shape_polygon1
        routers_population = []
        for routers in population:
            routers_without_overlap = self.resolve_router_overlap_solution(routers, radius, height, width,
                                                                           shape_polygon)
            routers_population.append(routers_without_overlap)
        return routers_population

    def run_algorithm(self, tk_screen2, algotype):
        # if algotype == 'PSO':
        # self.pso_algorithm()
        # elif
        if algotype == 'GA':
            self.thread = threading.Thread(target=self.ga_algorithm, args=(tk_screen2, 10000))
            self.thread.start()
        else:
            raise ValueError("Invalid algorithm type")

    def isItCovered(self, router, client, radius):
        distance = abs(math.sqrt(((router[0] - client.x) ** 2) + ((router[1] - client.y) ** 2)))
        return distance <= radius

    def findNewCoordinates(self, height, width, shape_polygon):
        new_x, new_y = 1, 1
        is_inside = -1.0
        if not self.check_image:
            new_x = random.uniform(0, int(width))
            new_y = random.uniform(0, int(height))
        while self.check_image and is_inside == -1.0:
            new_y = random.uniform(0, 1800)
            new_x = random.uniform(0, 1800)
            point = (new_x, new_y)
            is_inside = cv2.pointPolygonTest(shape_polygon, point, measureDist=False)
        new_router = (new_x, new_y)
        return new_router

    def continue_button(self):
        self.pause_event.clear()

    def pause_button(self):
        self.pause_event.set()

    # def pso_algorithm(self):
