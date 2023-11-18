import math
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle
import tkinter as tk


class Visual:
    def __init__(self, tk_screen2, algotype):
        self.original_image = None
        self.width = None
        self.height = None
        self.radius = None
        self.clients = None
        self.routers = None
        self.router_plot = None
        self.tk_screen2 = tk_screen2

        self.fig1 = Figure(figsize=(7, 7))
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.tk_screen2)
        self.ax1 = self.canvas1.figure.add_subplot(111)
        self.canvas_widget1 = self.canvas1.get_tk_widget()

        if algotype == 'GA':
            self.canvas_widget1.pack(side=tk.TOP, padx=0, pady=0)
        elif algotype == 'PSO':
            self.canvas_widget1.config(width=550, height=550)
            self.canvas_widget1.pack(side=tk.RIGHT, padx=20, pady=0)

            self.fig2 = Figure(figsize=(5.5, 5.5))
            self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.tk_screen2)
            self.ax2 = self.canvas2.figure.add_subplot(111)
            self.canvas_widget2 = self.canvas2.get_tk_widget()
            self.canvas_widget2.pack(side=tk.LEFT, padx=20, pady=0)

    def update_visualization_for_rect_PSO(self, routers, clients, radius, height, width):
        self.routers = routers
        self.clients = clients
        self.radius = radius
        self.height = height
        self.width = width

        # self.update_canvas2(swarm, combobox_number_particle)
        self.ax1.clear()

        x_coords = [router.x for router in self.routers.solution]
        y_coords = [router.y for router in self.routers.solution]
        self.ax1.scatter(x_coords, y_coords, marker='o', color='blue', label='Routers')

        client_x_coords = [client.x for client in self.clients if client.in_range]
        client_y_coords = [client.y for client in self.clients if client.in_range]
        self.ax1.scatter(client_x_coords, client_y_coords, marker='x', color='green', label='Clients covered')

        client_x_coords = [client.x for client in self.clients if not client.in_range]
        client_y_coords = [client.y for client in self.clients if not client.in_range]
        self.ax1.scatter(client_x_coords, client_y_coords, marker='x', color='black', label='Clients not covered')

        for x, y in zip(x_coords, y_coords):
            circle = Circle((x, y), self.radius, fill=False, color='red', linestyle='dotted', alpha=0.5, linewidth=2)
            self.ax1.add_patch(circle)

        self.ax1.set_xlim(0, int(self.height))
        self.ax1.set_ylim(0, int(self.width))
        self.fig1.subplots_adjust(right=0.84, top=0.84)
        self.ax1.legend(['Routers', 'Clients covered', 'Clients not covered'], loc='upper right',
                        bbox_to_anchor=(1.22, 1.22), fontsize=9)
        self.ax1.grid(True)

        self.canvas_widget1.update()
        self.canvas1.draw()
        #time.sleep(0.1)

    def update_canvas2(self, swarm, combobox_number_particle):
        self.ax2.clear()

        x_coords = [particle.x for particle in swarm]
        y_coords = [particle.y for particle in swarm]
        self.ax2.scatter(x_coords, y_coords, marker='o', color='green', label='Particle')

        self.ax2.set_xlim(0, 100)
        self.ax2.set_ylim(0, 100)
        self.fig2.subplots_adjust(right=0.84, top=0.84)

        self.ax2.grid(True)

        self.canvas_widget2.update()
        self.canvas2.draw()

    def update_visualization_for_image_GA(self, routers, clients, radius, original_image):
        self.routers = routers
        self.clients = clients
        self.radius = radius
        self.original_image = original_image

        self.ax1.clear()

        self.ax1.imshow(self.original_image, extent=[0, 1800, 1800, 0], aspect='auto')

        x_scale = self.canvas_widget1.winfo_width() * 2.55 / self.original_image.shape[1]
        y_scale = self.canvas_widget1.winfo_height() * 3.85 / self.original_image.shape[0]

        _, _ = self.original_image.shape[1], self.original_image.shape[0]

        x_coords = [router.x * x_scale for router in self.routers]
        y_coords = [router.y * y_scale for router in self.routers]
        self.ax1.scatter(x_coords, y_coords, marker='o', color='blue', label='Routers')

        client_x_coords = [client.x * x_scale for client in self.clients if client.in_range]
        client_y_coords = [client.y * y_scale for client in self.clients if client.in_range]
        self.ax1.scatter(client_x_coords, client_y_coords, marker='x', color='green', label='Clients covered')

        client_x_coords = [client.x * x_scale for client in self.clients if not client.in_range]
        client_y_coords = [client.y * y_scale for client in self.clients if not client.in_range]
        self.ax1.scatter(client_x_coords, client_y_coords, marker='x', color='black', label='Clients not covered')

        for x, y in zip(x_coords, y_coords):
            circle = Circle((x, y), self.radius, fill=False, color='red', linestyle='dotted', alpha=0.5, linewidth=2)
            self.ax1.add_patch(circle)

        self.ax1.set_xlim(0, 1800)
        self.ax1.set_ylim(1800, 0)
        self.fig1.subplots_adjust(right=0.9, top=0.9)
        self.ax1.legend(['Routers', 'Clients covered', 'Clients not covered'], loc='upper right', bbox_to_anchor=(1.1
                                                                                                                 , 1.1))
        self.ax1.grid(True)

        self.canvas_widget1.update()
        self.canvas1.draw()
        #if len(routers + clients) < 500:
            #time.sleep(0.1)

    def update_visualization_for_rect_GA(self, routers, clients, radius, height, width):
        self.routers = routers
        self.clients = clients
        self.radius = radius
        self.height = height
        self.width = width

        self.ax1.clear()

        x_coords = [router.x for router in self.routers]
        y_coords = [router.y for router in self.routers]
        self.ax1.scatter(x_coords, y_coords, marker='o', color='blue', label='Routers')

        client_x_coords = [client.x for client in self.clients if client.in_range]
        client_y_coords = [client.y for client in self.clients if client.in_range]
        self.ax1.scatter(client_x_coords, client_y_coords, marker='x', color='green', label='Clients covered')

        client_x_coords = [client.x for client in self.clients if not client.in_range]
        client_y_coords = [client.y for client in self.clients if not client.in_range]
        self.ax1.scatter(client_x_coords, client_y_coords, marker='x', color='black', label='Clients not covered')

        for x, y in zip(x_coords, y_coords):
            circle = Circle((x, y), self.radius, fill=False, color='red', linestyle='dotted', alpha=0.5, linewidth=2)
            self.ax1.add_patch(circle)

        self.ax1.set_xlim(0, int(self.height))
        self.ax1.set_ylim(0, int(self.width))
        self.fig1.subplots_adjust(right=0.8, top=0.8)
        self.ax1.legend(['Routers', 'Clients covered', 'Clients not covered'], loc='upper right', bbox_to_anchor=(1.3
                                                                                                                 , 1.3))
        self.ax1.grid(True)

        self.canvas_widget1.update()
        self.canvas1.draw()
        # time.sleep(0.1)

    def mark_covered_clients(self, routers, clients, radius):
        self.routers = routers
        self.clients = clients
        self.radius = radius

        for client in self.clients:
            client.in_range = False
            for router in self.routers:
                if self.check_coverage(router, client, radius):
                    client.in_range = True

    def check_coverage(self, router, client, radius):
        distance = abs(math.sqrt(((router.x - client.x) ** 2) + ((router.y - client.y) ** 2)))
        return distance <= radius
