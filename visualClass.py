from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle
import tkinter as tk

class Visual:
    def __init__(self, tk_screen2, height, width):
        self.radius = None
        self.clients = None
        self.routers = None
        self.tk_screen2 = tk_screen2
        self.height = height
        self.width = width
        self.fig = Figure(figsize=(4, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tk_screen2)
        self.ax = self.canvas.figure.add_subplot(111)
        self.canvas_widget = self.canvas.get_tk_widget()
        #self.canvas_widget.pack(side=tk.TOP, padx=80, pady=0)

    def update_visualization(self, routers, clients, radi):
        self.routers = routers
        self.clients = clients
        self.radius = radi

        #self.canvas_widget.delete("all")

        x_coords = [router[0] for router in self.routers]
        y_coords = [router[1] for router in self.routers]

        client_x_coords = [client.x for client in self.clients]
        client_y_coords = [client.y for client in self.clients]
        self.ax.scatter(x_coords, y_coords, marker='o', color='blue', label='Routers')
        self.ax.scatter(client_x_coords, client_y_coords, marker='x', color='green', label='Clients')

        for x, y in zip(x_coords, y_coords):
            circle = Circle((x, y), self.radius, fill=False, color='red', linestyle='dotted', alpha=0.5)
            self.ax.add_patch(circle)

        self.ax.set_xlim(0, int(self.width))
        self.ax.set_ylim(0, int(self.height))
        self.ax.legend()
        self.ax.grid(True)

        #self.canvas.draw()
        self.canvas_widget.pack(side=tk.TOP, padx=80, pady=0)

