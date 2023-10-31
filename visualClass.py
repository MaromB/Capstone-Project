import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle
import tkinter as tk
import algorithmClass


class Visual:
    def __init__(self, tk_screen2):
        self.original_image = None
        self.width = None
        self.height = None
        self.radius = None
        self.clients = None
        self.routers = None
        self.tk_screen2 = tk_screen2

        self.fig = Figure(figsize=(7, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tk_screen2)
        self.ax = self.canvas.figure.add_subplot(111)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, padx=80, pady=0)
        self.router_plot = None

    def update_visualization_for_rectangle(self, routers, clients, radius, height, width):
        self.routers = routers
        self.clients = clients
        self.radius = radius
        self.height = height
        self.width = width

        self.ax.clear()

        x_coords = [router[0] for router in self.routers]
        y_coords = [router[1] for router in self.routers]
        self.ax.scatter(x_coords, y_coords, marker='o', color='blue', label='Routers')

        client_x_coords = [client.x for client in self.clients if client.in_range]
        client_y_coords = [client.y for client in self.clients if client.in_range]
        self.ax.scatter(client_x_coords, client_y_coords, marker='x', color='green', label='Clients covered')

        client_x_coords = [client.x for client in self.clients if not client.in_range]
        client_y_coords = [client.y for client in self.clients if not client.in_range]
        self.ax.scatter(client_x_coords, client_y_coords, marker='x', color='black', label='Clients not covered')

        for x, y in zip(x_coords, y_coords):
            circle = Circle((x, y), self.radius, fill=False, color='red', linestyle='dotted', alpha=0.5, linewidth=2)
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

    def update_visualization_for_image(self, routers, clients, radius, original_image):
        self.routers = routers
        self.clients = clients
        self.radius = radius
        self.original_image = original_image

        self.ax.clear()

        self.ax.imshow(self.original_image, extent=[0, 1800, 1800, 0], aspect='auto')

        x_scale = self.canvas_widget.winfo_width() * 2.55 / self.original_image.shape[1]
        y_scale = self.canvas_widget.winfo_height() * 3.85 / self.original_image.shape[0]

        _, _ = self.original_image.shape[1], self.original_image.shape[0]

        x_coords = [router[0] * x_scale for router in self.routers]
        y_coords = [router[1] * y_scale for router in self.routers]
        self.ax.scatter(x_coords, y_coords, marker='o', color='blue', label='Routers')

        client_x_coords = [client.x * x_scale for client in self.clients if client.in_range]
        client_y_coords = [client.y * y_scale for client in self.clients if client.in_range]
        self.ax.scatter(client_x_coords, client_y_coords, marker='x', color='green', label='Clients covered')

        client_x_coords = [client.x * x_scale for client in self.clients if not client.in_range]
        client_y_coords = [client.y * y_scale for client in self.clients if not client.in_range]
        self.ax.scatter(client_x_coords, client_y_coords, marker='x', color='black', label='Clients not covered')

        for x, y in zip(x_coords, y_coords):
            circle = Circle((x, y), self.radius, fill=False, color='red', linestyle='dotted', alpha=0.5, linewidth=2)
            self.ax.add_patch(circle)

        self.ax.set_xlim(0, 1800)
        self.ax.set_ylim(1800, 0)
        self.fig.subplots_adjust(right=0.9, top=0.9)
        self.ax.legend(['Routers', 'Clients covered', 'Clients not covered'], loc='upper right', bbox_to_anchor=(1.1
                                                                                                                 , 1.1))
        self.ax.grid(True)

        self.canvas_widget.update()
        self.canvas.draw()
        if len(routers + clients) < 500:
            time.sleep(0.4)

    # update_visualization_for_photo(self.routers, self.clients, 5, self.num_photo)

    def mark_covered_clients(self, routers, clients, radius):
        self.routers = routers
        self.clients = clients
        self.radius = radius

        for client in self.clients:
            client.in_range = False
            for router in self.routers:
                if algorithmClass.Algorithm.isItCovered(self.tk_screen2, router, client, radius):
                    client.in_range = True
