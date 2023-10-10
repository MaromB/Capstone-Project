import math
import random

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Algorithm:
    def __init__(self, space, routers, clients, height, width):
        self.space = space
        self.routers = routers
        self.clients = clients
        self.height = height
        self.width = width

    #def pso_algorithm(self):
    def ga_algorithm(self, root2, max_iterations):

        current_population = self.initialize_population(20, self.space.routers, self.space.height, self.space.width)

        for iteration in range(max_iterations):
            # Evaluate the fitness of each solution in the population
            # fitness_scores = [space.fitness_function(space, current_population, client_locations) for client_locations in space.clients]
            fitness_scores = [self.fitness_function(self.space, current_population, self.space.clients) for _ in range(len(current_population))]
            # Select parents for crossover (you can use various selection methods)
            selected_parents = self.select_parents(current_population, fitness_scores)

            # Create a new population using crossover
            new_population = self.router_placement_crossover(selected_parents)

            # Apply mutation to some solutions in the new population
            mutated_population = self.mutate_population(new_population,0.05, self.height, self.width)

            # Evaluate the fitness of the mutated population
            mutated_fitness_scores = [self.fitness_function(self.space, mutated_population, client_locations) for client_locations in self.clients]

            # Replace the current population with the mutated population if it's better
            if self.space.is_better(mutated_fitness_scores, fitness_scores):
                current_population = mutated_population

            # Visualize the current state of the routers
            self.space.visualize_illustration(root2)

            # Return the best router locations found
        return current_population

    def fitness_function(self, router_locations, client_locations):

        total_coverage = 0
        for client in client_locations:
            is_covered = False
            for router in router_locations:
                if self.isItCovered(router, client):
                    is_covered = True
                    break
            if is_covered:
                total_coverage += 1

        return total_coverage / len(client_locations) * 100  # Return coverage as a percentage

    def initialize_population(self, num_solutions, num_routers, height, width):
        """
        Initialize a population of random solutions for the WMNs optimization problem.

        Parameters:
            num_solutions (int): Number of random solutions to generate.
            num_routers (int): Number of routers in each solution.
            height (int): Width of the area.
            width (int): Length of the area.

        Returns:
            List[List[Tuple[int, int]]]: A list of random solutions, where each solution is a list of (x, y) coordinates for routers.
        """
        population = []

        for _ in range(num_solutions):
            solution = []
            for _ in range(num_routers):
                x = random.randint(0, height)
                y = random.randint(0, width)
                solution.append((x, y))
            population.append(solution)

        return population

    def select_parents(self, population, fitness_scores, num_parents, tournament_size=3):
        selected_parents = []

        for _ in range(num_parents):
            # Perform tournament selection
            tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            selected_index = tournament_indices[np.argmax(tournament_fitness)]
            selected_parents.append(population[selected_index])

        return selected_parents
    def router_placement_crossover(self, selected_parents):

        new_population = []

        for i in range(0, len(selected_parents), 2):
            parent1 = selected_parents[i]
            parent2 = selected_parents[i + 1]

        # Randomly choose one of the parents as the base placement
        base_parent = parent1 if random.random() < 0.5 else parent2

        # Probability of inheriting each router position (adjust as needed)
        inherit_probability = 0.5

        # Iterate through router positions in the base parent
        for router_position in base_parent:
            # Decide whether to inherit this router position
            if random.random() < inherit_probability:
                new_population.append(router_position)

        # Fill in missing routers from the other parent
        other_parent = parent2 if base_parent == parent1 else parent1
        missing_routers = [router for router in other_parent if router not in new_population]
        random.shuffle(missing_routers)
        new_population.extend(missing_routers)

        return new_population

    def mutate_solution(self, solution, mutation_rate, height, width):

        mutated_solution = solution.copy()  # Make a copy of the solution to avoid modifying the original

        for router in mutated_solution:
            if random.random() < mutation_rate:
                # Generate new random positions for the router
                new_x = random.uniform(0, height)
                new_y = random.uniform(0, width)

                # Update the router's position with the new positions
                router.x = new_x
                router.y = new_y

        return mutated_solution

    def mutate_population(self, population, mutation_rate, height, width):
        mutated_population = []

        for solution in population:
            mutated_solution = population.mutate_solution(solution, mutation_rate, height, width)
            mutated_population.append(mutated_solution)

        return mutated_population

    def is_better(self, new_fitness_scores, old_fitness_scores):

        new_total_coverage = sum(new_fitness_scores)  # Calculate the total coverage of the new population
        old_total_coverage = sum(old_fitness_scores)

        return new_total_coverage > old_total_coverage

        # Calculate the coverage metric based on router locations and client locations
        # You can use your 'isItCovered' function to check coverage for each client
    def calculate_coverage(self, router_x, router_y, client_locations, radius):
        coverage_count = 0
        for client_x, client_y in client_locations:
            distance = ((router_x - client_x) ** 2 + (router_y - client_y) ** 2) ** 0.5
            if distance <= radius:
                coverage_count += 1
        return coverage_count
    def run_algorithm(self, root2, algotype):
        if algotype == 'PSO':
            self.pso_algorithm()
        elif algotype == 'GA':
            self.ga_algorithm(root2, 100)
        else:
            raise ValueError("Invalid algorithm type")

    def isItCovered(self, router, client):
        # Calculate the Euclidean distance between the router and client
        distance = math.sqrt((router.x - client.x) ** 2 + (router.y - client.y) ** 2)

        # Check if the distance is less than or equal to the router's coverage radius
        return distance <= router.radius