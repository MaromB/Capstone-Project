import math
import random
import tkinter as tk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Algorithm:
    def __init__(self, routers, clients, areah, areal):
        self.routers = routers
        self.clients = clients
        self.areah = areah
        self.areal = areal

    def pso_algorithm(self):
    def ga_algorithm(space, max_iterations, visualize_func):

        current_population = space.initialize_population(20, space.routers, space.areah, space.areal)

        for iteration in range(max_iterations):
            # Evaluate the fitness of each solution in the population
            # fitness_scores = [space.fitness_function(space, current_population, client_locations) for client_locations in space.clients]
            fitness_scores = [space.fitness_function(space, current_population, space.clients) for _ in range(len(current_population))]
            # Select parents for crossover (you can use various selection methods)
            selected_parents = space.select_parents(current_population, fitness_scores)

            # Create a new population using crossover
            new_population = space.crossover(selected_parents)

            # Apply mutation to some solutions in the new population
            mutated_population = space.mutate(new_population)

            # Evaluate the fitness of the mutated population
            mutated_fitness_scores = [space.fitness_function(space, mutated_population, client_locations) for client_locations in space.clients]

            # Replace the current population with the mutated population if it's better
            if is_better(mutated_fitness_scores, fitness_scores):
                current_population = mutated_population

            # Visualize the current state of the routers
            visualize_func(space, current_population)

            # Return the best router locations found
        return current_population

    def fitness_function(space, router_locations, client_locations):

        total_coverage = 0
        for client in client_locations:
            is_covered = False
            for router in router_locations:
                if space.isItCovered(router, client):
                    is_covered = True
                    break
            if is_covered:
                total_coverage += 1

        return total_coverage / len(client_locations) * 100  # Return coverage as a percentage

    def initialize_population(num_solutions, num_routers, areah, areal):
        """
        Initialize a population of random solutions for the WMNs optimization problem.

        Parameters:
            num_solutions (int): Number of random solutions to generate.
            num_routers (int): Number of routers in each solution.
            areah (int): Width of the area.
            areal (int): Length of the area.

        Returns:
            List[List[Tuple[int, int]]]: A list of random solutions, where each solution is a list of (x, y) coordinates for routers.
        """
        population = []

        for _ in range(num_solutions):
            solution = []
            for _ in range(num_routers):
                x = random.randint(0, areah)
                y = random.randint(0, areal)
                solution.append((x, y))
            population.append(solution)

        return population

    def select_parents(population, fitness_scores, num_parents, tournament_size=3):
        selected_parents = []

        for _ in range(num_parents):
            # Perform tournament selection
            tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            selected_index = tournament_indices[np.argmax(tournament_fitness)]
            selected_parents.append(population[selected_index])

        return selected_parents
        def crossover(parents):

        # Implement crossover to create new solutions from parents
        # You can use single-point crossover, two-point crossover, etc.

        def mutate(population):

        # Implement mutation to introduce small random changes to some solutions in the population

        def is_better(new_fitness_scores, old_fitness_scores):

        # Check if the new population is better than the old population based on fitness scores
        # You can use various criteria for this, such as comparing total coverage or other objectives

        def calculate_coverage(space, router_locations, client_locations):

    # Calculate the coverage metric based on router locations and client locations
    # You can use your 'isItCovered' function to check coverage for each client

    def run_algorithm(self, algotype):
        if algotype == 'PSO':
            self.pso_algorithm()
        elif algotype == 'GA':
            self.ga_algorithm()
        else:
            raise ValueError("Invalid algorithm type")

    def isItCovered(router, client):
        # Calculate the Euclidean distance between the router and client
        distance = math.sqrt((router.x - client.x) ** 2 + (router.y - client.y) ** 2)

        # Check if the distance is less than or equal to the router's coverage radius
        return distance <= router.radius