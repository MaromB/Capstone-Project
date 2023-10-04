import math
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Algorithm:
    def __init__(self, routers, clients, areah, areal):
        self.routers = routers
        self.clients = clients
        self.areah = areah
        self.areal = areal

    def pso_algorithm(self):
    def ga_algorithm(space, max_iterations, visualize_func):
        current_population = space.routers

        for iteration in range(max_iterations):
            # Evaluate the fitness of each solution in the population
            fitness_scores = [fitness_function(space, current_population, client_locations) for client_locations in space.clients]

            # Select parents for crossover (you can use various selection methods)
            selected_parents = select_parents(current_population, fitness_scores)

            # Create a new population using crossover
            new_population = crossover(selected_parents)

            # Apply mutation to some solutions in the new population
            mutated_population = mutate(new_population)

            # Evaluate the fitness of the mutated population
            mutated_fitness_scores = [fitness_function(space, mutated_population, client_locations) for client_locations in space.clients]

            # Replace the current population with the mutated population if it's better
            if is_better(mutated_fitness_scores, fitness_scores):
                current_population = mutated_population

            # Visualize the current state of the routers
            visualize_func(space, current_population)

            # Return the best router locations found
        return current_population

        def fitness_function(space, router_locations, client_locations):
            # Calculate the coverage metric based on router locations and client locations
            coverage = calculate_coverage(space, router_locations, client_locations)

            # Calculate some other objective function if needed
            # For example, you may want to maximize coverage while minimizing the number of routers used

            return coverage  # Adjust this based on your specific objective

        def select_parents(population, fitness_scores):

        # Implement a selection method to choose parents based on fitness scores
        # You can use roulette wheel selection, tournament selection, etc.

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