import random
import cv2
from router_Class import Router
from client_Class import Client

class Area:
    def __init__(self, height=None, width=None):
        self.height = height
        self.width = width
        self.routers = []
        self.clients = []

    def generate_random_routers_and_clients(self, n_routers, n_clients, router_radius):
        self.routers = []
        self.clients = []

        for _ in range(n_routers):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            router = Router(x, y, router_radius)
            self.routers.append(router)

        for _ in range(n_clients):
            y = random.uniform(0, self.height)
            x = random.uniform(0, self.width)
            client = Client(x, y)
            self.clients.append(client)
        return

    def generate_random_clients(self, n_clients):
        self.clients = []
        for _ in range(n_clients):
            y = random.uniform(0, self.height)
            x = random.uniform(0, self.width)
            client = Client(x, y)
            self.clients.append(client)

    def generate_random_clients_for_photo(self, n_clients, shape_polygon):
        self.clients = []
        while True:
            y = random.uniform(0, 1800)
            x = random.uniform(0, 1800)
            point = (x, y)
            is_inside = cv2.pointPolygonTest(shape_polygon, point, measureDist=False)
            if is_inside == 1:
                self.clients.append(Client(x, y))
            if len(self.clients) == n_clients:
                break

