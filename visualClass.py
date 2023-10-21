import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle
import tkinter as tk

import algorithmClass


class Visual:
    def __init__(self, tk_screen2, height, width):
        self.radius = None
        self.clients = None
        self.routers = None
        self.tk_screen2 = tk_screen2
        self.height = height
        self.width = width
        self.fig = Figure(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tk_screen2)
        self.ax = self.canvas.figure.add_subplot(111)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, padx=80, pady=0)
        self.router_plot = None

    def update_visualization(self, routers, clients, radius):
        self.routers = routers
        self.clients = clients
        self.radius = radius

        self.canvas_widget = self.canvas.get_tk_widget()
        self.ax.clear()

        x_coords = [router[0] for router in self.routers]
        y_coords = [router[1] for router in self.routers]
        self.ax.scatter(x_coords, y_coords, marker='o', color='blue', label='Routers')

        client_x_coords = [client.x for client in self.clients if client.in_range]
        client_y_coords = [client.y for client in self.clients if client.in_range]
        self.ax.scatter(client_x_coords, client_y_coords, marker='x', color='black', label='Clients covered')

        client_x_coords = [client.x for client in self.clients if not client.in_range]
        client_y_coords = [client.y for client in self.clients if not client.in_range]
        self.ax.scatter(client_x_coords, client_y_coords, marker='x', color='green', label='Clients not covered')

        for x, y in zip(x_coords, y_coords):
            circle = Circle((x, y), self.radius, fill=False, color='red', linestyle='dotted', alpha=0.5)
            self.ax.add_patch(circle)

        self.ax.set_xlim(0, int(self.height))
        self.ax.set_ylim(0, int(self.width))
        self.fig.subplots_adjust(right=0.8, top=0.8)
        self.ax.legend(['Routers', 'Clients covered', 'Clients not covered'], loc='upper right', bbox_to_anchor=(1.3
                                                                                                                 , 1.3))
        self.ax.grid(True)

        self.canvas_widget.update()
        self.canvas.draw()
        time.sleep(0.4)

    def mark_covered_clients(self, routers, clients, radius):
        self.routers = routers
        self.clients = clients
        self.radius = radius

        for client in self.clients:
            client.in_range = False
            for router in self.routers:
                if algorithmClass.Algorithm.isItCovered(self, router, client, radius):
                    client.in_range = True
