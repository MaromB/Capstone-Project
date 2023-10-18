import math
import random
from visualClass import Visual
import numpy as np

class Algorithm:
    def __init__(self, space, routers, clients, height, width, second_screen):
        self.visual = None
        self.space = space
        self.routers = routers
        self.clients = clients
        self.height = height
        self.width = width
        self.second_screen = second_screen
        self.current_population = self.initialize_population(20, int(self.routers), self.space.height, self.space.width)
        self.clients = self.clients

    def ga_algorithm(self, tk_screen2, max_iterations, second_screen):
        def iteration_callback(iteration):
            if iteration < max_iterations:
                # Evaluate the fitness of each solution in the population
                fitness_scores = self.fitness_function(self.current_population, self.clients, 5)
                # Select parents for crossover (you can use various selection methods)
                descendants = self.select_parents(self.current_population, fitness_scores, int(len(fitness_scores)/2))
                # Create a new population using crossover
                new_population = self.router_placement_crossover(descendants)
                # Apply mutation to some solutions in the new population
                mutated_population = self.mutate_population(new_population,0.2, self.height, self.width)
                resolved_routers = self.resolve_router_overlap_population(mutated_population, 5 , self.height, self.width)
                # Evaluate the fitness of the mutated population
                mutated_fitness_scores = self.fitness_function(resolved_routers, self.clients, 5)
                # Replace the current population with the mutated population if it's better
                if self.is_better(mutated_fitness_scores, fitness_scores):
                    self.current_population = resolved_routers
                    fitness_scores = mutated_fitness_scores
                # Visualize the best current state of the routers
                best_current_state = self.best_configuration_output(self.current_population, fitness_scores)
                self.routers = best_current_state
                if not self.visual:
                    self.visual = Visual(tk_screen2, self.height, self.width)
                self.visual.update_visualization(self.routers, self.clients, 5)
                print("iteration number: " + str(iteration))
                tk_screen2.after(1, iteration_callback, iteration + 1)
            else:
                print("done")
                return self.current_population

        iteration_callback(0)

    def fitness_function(self, current_population, client_locations, radius):
        total_coverage = []
        for routers in current_population:
            counter = 0
            for router in routers:
                for client in client_locations:
                    if self.isItCovered(router, client, radius):
                        counter += 1
            total_coverage.append(counter/len(client_locations) * 100)

        return total_coverage

    def initialize_population(self, num_solutions, routers, height, width):
        population = []

        for _ in range(num_solutions):
            solution = []
            for _ in range(routers):
                x = random.randint(0, height)
                y = random.randint(0, width)
                solution.append((x, y))
            population.append(solution)

        return population

    def select_parents(self, population, fitness_scores, num_parents, tournament_size=5):
        selected_parents = []

        while len(selected_parents) < num_parents:
            # Perform tournament selection
            tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            selected_index = tournament_indices[np.argmax(tournament_fitness)]

            if population[selected_index] not in selected_parents:
                selected_parents.append(population[selected_index])

        return selected_parents

    def router_placement_crossover(self, selected_parents):

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

    def mutate_solution(self, solution, mutation_rate, height, width):
        mutated_solution = []
        for router_x, router_y in solution:
            if random.random() < mutation_rate:
                # Generate new random positions for the router
                new_x = random.uniform(0, int(height))
                new_y = random.uniform(0, int(width))
            else:
                new_x = router_x
                new_y = router_y

            # Add the mutated router to the new list
            mutated_solution.append((int(new_x), int(new_y)))

        return mutated_solution

    def mutate_population(self, population, mutation_rate, height, width):
        mutated_population = []

        for solution in population:
            mutated_solution = self.mutate_solution(solution, mutation_rate, height, width)
            mutated_population.append(mutated_solution)

        return mutated_population

    def resolve_router_overlap_solution(self, routers, radius, height, width):
        resolved_routers = []
        resolved_routers.append(routers[0])
        new_router = ()
        for router in routers[1:]:
            overlapping = False
            if self.checkOverlapForOneRouter(router, resolved_routers, radius):
                    new_router = self.findNewCoordinates(router, radius, height, width)
                    overlapping = True
            if overlapping:
                while self.checkOverlapForOneRouter(new_router, resolved_routers, radius):
                    new_router = self.findNewCoordinates(new_router, radius, height, width)
                resolved_routers.append(new_router)
            else:
                resolved_routers.append(router)

        return resolved_routers
    def resolve_router_overlap_population(self, population, radius, height, width):
        routers_population = []
        for routers in population:
            routers_without_overlap = self.resolve_router_overlap_solution(routers, radius, height, width)
            routers_population.append(routers_without_overlap)

        return routers_population

    def is_better(self, new_fitness_scores, old_fitness_scores):
        new_total_coverage = sum(new_fitness_scores)  # Calculate the total coverage of the new population
        old_total_coverage = sum(old_fitness_scores)

        return new_total_coverage > old_total_coverage

    def calculate_coverage(self, router_x, router_y, client_locations, radius):
        coverage_count = 0
        for client_x, client_y in client_locations:
            distance = ((router_x - client_x) ** 2 + (router_y - client_y) ** 2) ** 0.5
            if distance <= radius:
                coverage_count += 1
        return coverage_count

    def best_configuration_output(self, current_population, fitness_scores):
        best_conf = []
        index = 0
        for i in range(len(current_population)):
           if fitness_scores[index] < fitness_scores[i]:
              index = i
        best_conf = current_population[index]

        return best_conf

    def run_algorithm(self, tk_screen2, algotype, second_screen):
        if algotype == 'PSO':
            self.pso_algorithm()
        elif algotype == 'GA':
            self.ga_algorithm(tk_screen2, 1000, second_screen)
        else:
            raise ValueError("Invalid algorithm type")

    def isItCovered(self, router, client, radius):
        distance = abs(math.sqrt(((router[0] - client.x) ** 2) + ((router[1] - client.y) ** 2)))
        return distance <= radius

    def checkOverlapForOneRouter(self, router1, routers, radius):
        for router2 in routers:
            if self.distanceBetweenRouters(router1, router2, radius):
                return True
        return False

    def findNewCoordinates(self, router, radius, height, width):

        while True:
            new_x = router[0] + random.randint(-radius, radius)
            new_y = router[1] + random.randint(-radius, radius)
            new_router = (new_x, new_y)
            if (new_x > 0 and new_x < int(height)) and (new_y > 0 and new_y < int(width)):
                break

        return new_router

    def distanceBetweenRouters(self, router1, router2, radius):
        distance = abs(math.sqrt(((router1[0] - router2[0]) ** 2)+((router1[1] - router2[1]) ** 2)))
        return distance <= 2*radius



    # def pso_algorithm(self):