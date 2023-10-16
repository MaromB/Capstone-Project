import random
from routerClass import Router
from clientClass import Client

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
        return

    def generate_random_clients(self, n_clients):
        self.clients = []

        for _ in range(n_clients):
            # Generate random x and y coordinates for clients within the space
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            # Create a client with the random coordinates
            client = Client(x, y)
            self.clients.append(client)
        return