import random
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from routerClass import Router  # Import the Router class from routerClass.py
from clientClass import Client  # Import the Router class from routerClass.py
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

class Area:
    def __init__(self, width, height):
        self.width = width  # Width of the space
        self.height = height  # Height of the space
        self.routers = []  # A list to store the generated routers.
        self.clients = []  # A list to store the generated clients

    def generate_random_routers_and_clients(self, n_routers, n_clients, router_radius):
        self.routers = []  # Clear any existing routers
        self.clients = []  # Clear any existing clients

        for _ in range(n_routers):
            # Generate random x and y coordinates for routers within the space
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)

            # Create a router with the random coordinates and radius
            router = Router(x, y, router_radius)
            self.routers.append(router)

        for _ in range(n_clients):
            # Generate random x and y coordinates for clients within the space
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            # Create a client with the random coordinates
            client = Client(x, y)
            self.clients.append(client)
    def visualize_routers(self, root2):
        # Create a scatter plot to visualize routers
        x_coords = [router.x for router in self.routers]
        y_coords = [router.y for router in self.routers]
        radii = [router.radius for router in self.routers]

        fig, ax = plt.subplots(figsize=(4, 4))
        root2.configure(bg="light sky blue")

        client_x_coords = [client.x for client in self.clients]
        client_y_coords = [client.y for client in self.clients]
        ax.scatter(x_coords, y_coords, marker='o', color='blue', label='Routers')
        ax.scatter(client_x_coords, client_y_coords, marker='x', color='green', label='Clients')

        # Add circles to represent the coverage radius of each router
        for x, y, radius in zip(x_coords, y_coords, radii):
            circle = Circle((x, y), radius, fill=False, color='red', linestyle='dotted', alpha=0.5)
            ax.add_patch(circle)

        plt.xlim(0, self.width)
        plt.ylim(0, self.height)
        plt.legend()
        plt.grid(True)

        # Embed the Matplotlib figure in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=root2)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, padx=80, pady=0)
