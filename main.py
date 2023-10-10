import tkinter as tk
from tkinter import ttk
from areaClass import Area
from algorithmClass import Algorithm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from routerClass import Router  # Import the Router class from routerClass.py

class FirstScreen(tk.Frame):
    def __init__(self, parent, show_second_screen):
        super().__init__(parent)
        self.show_second_screen = show_second_screen

        # Get screen width and height
        screen_width = self.master.winfo_screenwidth()  # Fix here
        screen_height = self.master.winfo_screenheight()  # Fix here

        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2

        # Set window size and position
        self.master.geometry(f'1000x700+{x + 100}+{y-50}')
        style = ttk.Style()
        style.configure("Custom.TFrame", background="light sky blue")

        custom_font = ("Ariel", 18)
        custom_font2 = ("Ariel", 20, "bold")
        style.configure("Custom.TButton", font=custom_font)
        self.configure(bg="light sky blue")

        self.pack(fill=tk.BOTH, expand=True)

        self.label_Space = ttk.Label(self, text=" ", background="light sky blue")
        self.label_Following = ttk.Label(self, text="Please insert the following:", font=custom_font2, background="light sky blue")
        self.label_Routers = ttk.Label(self, text="Number of mesh routers:", font=custom_font, background="light sky blue")
        self.entry_Routers = ttk.Entry(self)
        self.label_Clients = ttk.Label(self, text="Numer of clients:", font=custom_font, background="light sky blue")
        self.entry_Clients = ttk.Entry(self)
        self.label_Size = ttk.Label(self, text="Size of area:", font=custom_font, background="light sky blue")
        self.entry_SizeH = ttk.Entry(self)
        self.label_SizeX = ttk.Label(self, text=" x ", font=custom_font, background="light sky blue")
        self.entry_SizeL = ttk.Entry(self)
        self.label_algorithem = ttk.Label(self, text="Algorithem:", font=custom_font, background="light sky blue")
        self.algorithm_combobox = ttk.Combobox(self, width=15)
        self.algorithm_combobox['values'] = ('', 'GA', 'PSO')
        self.run_button = ttk.Button(self, text="Run", command=self.switch_to_second_screen, style="Custom.TButton")

        # Use grid layout to place GUI elements
        self.label_Space.grid(row=1, column=0, padx=0, pady=30, sticky=tk.W)
        self.label_Following.grid(row=2, column=0, padx=20, pady=70, sticky=tk.W)
        self.label_Routers.grid(row=3, column=0, padx=20, pady=0, sticky=tk.W)
        self.entry_Routers.grid(row=3, column=1, padx=0, pady=10, sticky=tk.W)
        self.label_Clients.grid(row=4, column=0, padx=20, pady=20, sticky=tk.W)
        self.entry_Clients.grid(row=4, column=1, padx=0, pady=10, sticky=tk.W)
        self.label_Size.grid(row=5, column=0, padx=20, pady=0, sticky=tk.W)
        self.entry_SizeH.grid(row=5, column=1, padx=0, pady=0, sticky=tk.W)
        self.label_SizeX.grid(row=5, column=2, padx=0, pady=0, sticky=tk.W)
        self.entry_SizeL.grid(row=5, column=3, padx=0, pady=0, sticky=tk.W)
        self.label_algorithem.grid(row=6, column=0, padx=20, pady=15, sticky=tk.W)
        self.algorithm_combobox.grid(row=6, column=1, padx=0, pady=0)
        self.run_button.grid(row=7, columnspan=100, padx=400, pady=100)

    def switch_to_second_screen(self):
        routers = self.entry_Routers.get()
        clients = self.entry_Clients.get()
        height = self.entry_SizeH.get()
        width = self.entry_SizeL.get()
        algotype = self.algorithm_combobox.get()
        self.show_second_screen(routers, clients, height, width, algotype)

class SecondScreen(tk.Frame):
    def __init__(self, parent, routers, clients, height, width, algotype):
        super().__init__(parent)
        self.routers = routers
        self.clients = clients
        self.height = height
        self.width = width
        self.algotype = algotype

        root2 = tk.Toplevel()  # Create a new window (second screen)
        root2.title("WMNs Optimization - map")
        style = ttk.Style()
        style.configure("Custom.TFrame", background="light sky blue")

        # Get screen width and height
        screen_width = root2.winfo_screenwidth()
        screen_height = root2.winfo_screenheight()

        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2

        # Set window size and position
        root2.geometry(f'1000x700+{x + 100}+{y - 50}')
        lable_font = ("Ariel", 20, "bold")
        custom_font = ("Ariel", 14)

        info_frame1 = ttk.Frame(root2, style="Custom.TFrame")
        info_frame1.pack(side=tk.TOP, anchor=tk.S, padx=80, pady=20)
        info_frame2 = ttk.Frame(root2, style="Custom.TFrame")
        info_frame2.pack(side=tk.TOP, anchor=tk.W, padx=20, pady=20)
        info_frame3 = ttk.Frame(root2, style="Custom.TFrame")
        info_frame3.pack(side=tk.BOTTOM, anchor=tk.S, padx=0, pady=10)
        self.top_label = ttk.Label(info_frame1, text="Optimization of routers placements in WMNs", font=lable_font, background="light sky blue")
        self.running_algorithm = ttk.Label(info_frame2, text="Running algorithm:", font=custom_font, background="light sky blue")
        self.name_algorithm = ttk.Label(info_frame2, text=self.algotype, font=custom_font, background="light sky blue")
        self.iteration_label = ttk.Label(info_frame2, text="Iteration number:            0", font=custom_font, background="light sky blue")
        self.coverage_label = ttk.Label(info_frame2, text="Coverage:                       0%", font=custom_font, background="light sky blue")
        self.details_label = ttk.Label(info_frame3, text=f"For  {routers}  routers, {clients}  clients and  {height}  X  {width}  area size", font=custom_font, background="light sky blue")
        self.continue_button = ttk.Button(info_frame3, text="Continue", command=self.keep_optimization, style="Custom.TButton")
        self.stop_button = ttk.Button(info_frame3, text="Stop", command=self.stop_optimization, style="Custom.TButton")

        self.top_label.grid(row=0, column=0, padx=0, pady=10)
        self.running_algorithm.grid(row=1, column=0, padx=0, pady=10, sticky=tk.W)
        self.name_algorithm.grid(row=1, column=1, padx=0, pady=0, sticky=tk.W)
        self.iteration_label.grid(row=2, column=0, padx=0, pady=10, sticky=tk.W)
        self.coverage_label.grid(row=3, column=0, padx=0, pady=10, sticky=tk.W)
        self.details_label.grid(row=1, column=1, padx=0, pady=20)
        self.continue_button.grid(row=2, column=1, padx=(200, 0), pady=0)
        self.stop_button.grid(row=2, column=1, padx=(0, 200), pady=0)

        self.space = Area(int(self.height), int(self.width))
        self.algorithm = Algorithm(self.space, self.routers, self.clients, self.height, self.height)
        self.space.generate_random_routers_and_clients(int(self.routers), int(self.clients), 5)
        self.space.visualize_illustration(root2)
        self.algorithm.run_algorithm(root2, algotype)


    def update_labels(self, coverage_percentage, iteration_number):
        # Update labels with the latest values
        self.iteration_label.config(text=f"Iteration:                {iteration_number}")
        self.coverage_label.config(text=f"Coverage:            {coverage_percentage}%")

    def stop_optimization(self):
        # Implement the logic to stop the optimization process
        pass

    def keep_optimization(self):
        # Implement the logic to keep the optimization process
        pass


class OptimizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WMNs Optimization")

        # Initialize parameters
        self.routers = None
        self.clients = None

        # Create an instance of the FirstScreen class and show it
        self.first_screen = FirstScreen(self.root, self.show_second_screen)
        self.first_screen.pack()

    def show_second_screen(self, routers, clients, height, width, algotype):
        SecondScreen(self.root, routers, clients, height, width, algotype)
        #self.first_screen.destroy()  # Close the first screen

def main():
    root = tk.Tk()
    OptimizationApp(root)
    root.mainloop()

if __name__ == '__main__':
        main()

'''
    def run_pso(self):
        # PSO implementation
        particles = initialize_particles()  # You need to implement this

        for iteration in range(self.num_iterations):
            for particle in particles:
                # Update velocity and position
                update_velocity_and_position(particle)  # You need to implement this

                # Evaluate fitness
                particle.fitness = evaluate_fitness(particle.position)  # You need to implement this

            # Update global best
            update_global_best(particles)  # You need to implement this

        return global_best_solution   
'''

'''
    def run_ga(self):
        # GA implementation
        # Initialization
        population = initialize_population(self.population_size, self.chromosome_length)

        global_best_solution = None
        global_best_fitness = float('-inf')

        for iteration in range(self.num_iterations):
            # Evaluation
            fitness_scores = evaluate_population(population)

            # Track best solution in this iteration
            best_index = fitness_scores.index(max(fitness_scores))
            iteration_best_solution = population[best_index]
            iteration_best_fitness = fitness_scores[best_index]

            # Update global best if needed
            if iteration_best_fitness > global_best_fitness:
                global_best_solution = iteration_best_solution
                global_best_fitness = iteration_best_fitness

            # Selection, Crossover, Mutation
            selected_parents = select_parents(population, fitness_scores, self.num_parents)
            new_generation = crossover_and_mutate(selected_parents, len(population) - self.num_parents,
                                                  self.mutation_rate)

            # Replace old population with new generation
            population = selected_parents + new_generation

        return global_best_solution


    def run_optimization(self):
        if self.optimization_choice.get() == "GA":
            best_solution = self.run_ga()
        elif self.optimization_choice.get() == "PSO":
            best_solution = self.run_pso()

        self.plot_results(best_solution)

    def plot_results(self):
        # Create a figure and axis using matplotlib
        fig, ax = plt.subplots()

        # Plot router and user positions, connecting lines, etc.
        # ...

        # Create a canvas widget to embed the matplotlib plot in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()


def initialize_population(pop_size, chromosome_length):
    population = []
    for _ in range(pop_size):
        chromosome = [random.uniform(0, 1) for _ in range(chromosome_length)]
        population.append(chromosome)
    return population


def evaluate_population(population):
    fitness_scores = []
    for chromosome in population:
        # Calculate fitness based on your objective function
        fitness = calculate_fitness(chromosome)  # You need to implement this
        fitness_scores.append(fitness)
    return fitness_scores


def select_parents(population, fitness_scores, num_parents):
    parents = []
    # Select parents based on fitness (you can use various selection methods)
    # For simplicity, let's use a basic proportional selection
    total_fitness = sum(fitness_scores)
    probabilities = [fitness / total_fitness for fitness in fitness_scores]

    for _ in range(num_parents):
        selected_index = roulette_wheel_selection(probabilities)
        parents.append(population[selected_index])
    return parents


def roulette_wheel_selection(probabilities):
    random_value = random.uniform(0, 1)
    total_prob = 0
    for index, prob in enumerate(probabilities):
        total_prob += prob
        if total_prob >= random_value:
            return index


def crossover_and_mutate(parents, num_offspring, mutation_rate):
    offspring = []
    while len(offspring) < num_offspring:
        parent1, parent2 = random.sample(parents, 2)
        crossover_point = random.randint(1, len(parent1) - 1)
        child = parent1[:crossover_point] + parent2[crossover_point:]

        if random.uniform(0, 1) < mutation_rate:
            mutation_point = random.randint(0, len(child) - 1)
            child[mutation_point] = random.uniform(0, 1)

        offspring.append(child)
    return offspring
   '''
