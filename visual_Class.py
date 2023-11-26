import math
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle
import tkinter as tk


class Visual:
    def __init__(self, second_screen, tk_screen2, algotype, check_image):
        self.canvas_widget = None
        self.canvas = None
        self.ax = None
        self.check_image = None
        self.original_image = None
        self.width = None
        self.height = None
        self.radius = None
        self.clients = None
        self.routers = None
        self.router_plot = None
        self.tk_screen2 = tk_screen2
        self.second_screen = second_screen
        self.check_image = check_image

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

    def update_parameters(self, routers, clients, radius, algo, type_of, height, width, original_image):
        if algo == 'PSO':
            if type_of == 'global':
                self.update_visualization_for_rect_PSO(routers, clients, radius, height, width, self.ax2,
                                                       self.canvas_widget2, self.canvas2)
            elif type_of == 'global image':
                self.update_visualization_for_image(routers, clients, radius, original_image, self.ax2,
                                                    self.canvas_widget2, self.canvas2, 'PSO')
                self.fig2.subplots_adjust(right=0.9, top=0.9)
            elif type_of == 'Particles image':
                self.update_visualization_for_image(routers, clients, radius, original_image, self.ax1,
                                                    self.canvas_widget1, self.canvas1, 'PSO')
            else:
                self.update_visualization_for_rect_PSO(routers, clients, radius, height, width, self.ax1,
                                                       self.canvas_widget1, self.canvas1)
        elif algo == 'GA':
            if type_of == 'image':
                self.update_visualization_for_image(routers, clients, radius, original_image, self.ax1,
                                                    self.canvas_widget1, self.canvas1, 'GA')
            elif type_of == 'rect':
                self.update_visualization_for_rect_GA(routers, clients, radius, height, width)

    def update_visualization_for_rect_PSO(self, routers, clients, radius, height, width, ax, canvas_widget, canvas):
        self.routers = routers
        self.clients = clients
        self.radius = radius
        self.height = height
        self.width = width
        self.ax = ax
        self.canvas_widget = canvas_widget
        self.canvas = canvas

        self.ax.clear()

        x_coords = [router.x for router in self.routers]
        y_coords = [router.y for router in self.routers]
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

        self.ax.set_xlim(0, int(self.width))
        self.ax.set_ylim(0, int(self.height))
        
        self.fig1.subplots_adjust(right=0.84, top=0.84)
        self.fig2.subplots_adjust(right=0.84, top=0.84)
        self.ax.legend(['Routers', 'Clients covered', 'Clients not covered'], loc='upper right',
                       bbox_to_anchor=(1.22, 1.22), fontsize=9)
        self.ax.grid(True)

        self.canvas_widget.update()
        self.canvas.draw()
        sleep_time = float(self.second_screen.speed_var.get()) / 100.0
        time.sleep(sleep_time)

    def update_visualization_for_image(self, routers, clients, radius, original_image, ax, canvas_widget, canvas,
                                       algo):
        self.routers = routers
        self.clients = clients
        self.radius = radius
        self.original_image = original_image
        self.ax = ax
        self.canvas_widget = canvas_widget
        self.canvas = canvas

        self.ax.clear()

        self.ax.imshow(self.original_image, extent=[0, 1800, 1800, 0], aspect='auto')
        if algo == 'PSO':
            x_scale = self.canvas_widget1.winfo_width() * 3.2 / self.original_image.shape[1]
            y_scale = self.canvas_widget1.winfo_height() * 4.3 / self.original_image.shape[0]
        else:
            x_scale = self.canvas_widget1.winfo_width() * 2.55 / self.original_image.shape[1]
            y_scale = self.canvas_widget1.winfo_height() * 4.25 / self.original_image.shape[0]

        _, _ = self.original_image.shape[1], self.original_image.shape[0]

        x_coords = [router.x * x_scale for router in self.routers]
        y_coords = [router.y * y_scale for router in self.routers]
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
        self.fig1.subplots_adjust(right=0.9, top=0.9)
        self.ax.legend(['Routers', 'Clients covered', 'Clients not covered'], loc='upper right', bbox_to_anchor=(1.1
                                                                                                                 , 1.1))
        self.ax.grid(True)

        self.canvas_widget.update()
        self.canvas.draw()
        sleep_time = float(self.second_screen.speed_var.get()) / 100.0
        time.sleep(sleep_time)

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

        self.ax1.set_xlim(0, int(self.width))
        self.ax1.set_ylim(0, int(self.height))
        self.fig1.subplots_adjust(right=0.8, top=0.8)
        self.ax1.legend(['Routers', 'Clients covered', 'Clients not covered'], loc='upper right', bbox_to_anchor=(1.3
                                                                                                                 , 1.3))
        self.ax1.grid(True)

        self.canvas_widget1.update()
        self.canvas1.draw()
        sleep_time = float(self.second_screen.speed_var.get()) / 100.0
        time.sleep(sleep_time)

    def mark_covered_clients(self, routers, clients, radius):
        self.routers = routers
        self.clients = clients
        self.radius = radius

        for client in self.clients:
            client.in_range = False
            for router in self.routers:
                if self.check_coverage(router, client, radius):
                    client.in_range = True

    @staticmethod
    def check_coverage(router, client, radius):
        distance = abs(math.sqrt(((router.x - client.x) ** 2) + ((router.y - client.y) ** 2)))
        return distance <= radius

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
