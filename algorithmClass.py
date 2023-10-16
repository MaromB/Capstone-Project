import math
import random
import time
from visualClass import Visual
from areaClass import Area
import numpy as np

class Algorithm:
    def __init__(self, space, routers, clients, height, width, second_screen,):
        self.visual = None
        self.space = space
        self.routers = routers
        self.clients = clients
        self.height = height
        self.width = width
        self.second_screen = second_screen

    def ga_algorithm(self, tk_screen2, max_iterations, second_screen):

        current_population = self.initialize_population(20, int(self.routers), self.space.height, self.space.width)
        clients = self.clients
        for iteration in range(max_iterations):
            # Evaluate the fitness of each solution in the population
            fitness_scores = self.fitness_function(current_population, clients, 5)
            # Select parents for crossover (you can use various selection methods)
            selected_parents = self.select_parents(current_population, fitness_scores, int(len(fitness_scores)/2))
            # Create a new population using crossover
            new_population = self.router_placement_crossover(selected_parents)

            # Apply mutation to some solutions in the new population
            mutated_population = self.mutate_population(new_population,0.05, self.height, self.width)

            # Evaluate the fitness of the mutated population
            mutated_fitness_scores = self.fitness_function(mutated_population, clients, 5)
            # Replace the current population with the mutated population if it's better
            if self.is_better(mutated_fitness_scores, fitness_scores):
                current_population = mutated_population
                fitness_scores = mutated_fitness_scores

            # Visualize the best current state of the routers
            best_current_state = self.best_configuration_output(current_population, fitness_scores)
            self.routers = best_current_state
            if not self.visual:
                self.visual = Visual(tk_screen2, self.height, self.width)

            self.visual.update_visualization(self.routers, clients, 5)
            time.sleep(1)
            print("hi")

        second_screen.mainloop()
        return current_population

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

                if len(cur_list) == 10:
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
            self.ga_algorithm(tk_screen2, 100, second_screen)
        else:
            raise ValueError("Invalid algorithm type")

    def isItCovered(self, router, client, radius):
        # Calculate the Euclidean distance between the router and client
        distance = abs(math.sqrt((router[0] - client.x) ** 2 + (router[1] - client.y) ** 2))

        # Check if the distance is less than or equal to the router's coverage radius
        return distance <= radius

    # def pso_algorithm(self):