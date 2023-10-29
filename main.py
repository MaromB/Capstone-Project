import tkinter as tk
from tkinter import ttk
from areaClass import Area
from algorithmClass import Algorithm
from imageClass import ImageManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class FirstScreen(tk.Frame):
    def __init__(self, parent, show_second_screen):
        super().__init__(parent)
        self.show_second_screen = show_second_screen

        screen_height = self.master.winfo_screenheight()
        screen_width = self.master.winfo_screenwidth()

        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2

        # Set window size and position
        self.master.geometry(f'1000x700+{x + 100}+{y - 50}')
        style = ttk.Style()

        custom_font = ("Ariel", 18)
        custom_font2 = ("Ariel", 20, "bold")
        custom_font3 = ("Ariel", 12)
        style.configure("Custom.TButton", font=custom_font, background="light sky blue")
        style.configure("Checkbutton", font=custom_font, background="light sky blue")
        self.configure(bg="light sky blue")

        self.pack(fill=tk.BOTH, expand=True)
        self.check_image = tk.BooleanVar()

        self.label_Space = ttk.Label(self, text=" ", background="light sky blue")
        self.label_of_project = ttk.Label(self, text="Optimization of routers placements in WMNs:", font=custom_font2,
                                          background="light sky blue")
        self.label_Following = ttk.Label(self, text="Please insert the following:", font=custom_font,
                                         background="light sky blue")
        self.label_Routers = ttk.Label(self, text="Number of mesh routers:", font=custom_font,
                                       background="light sky blue")
        self.entry_Routers = ttk.Entry(self, width=7)
        self.label_Clients = ttk.Label(self, text="Numer of clients:", font=custom_font, background="light sky blue")
        self.entry_Clients = ttk.Entry(self, width=7)
        self.label_Size = ttk.Label(self, text="Size of area:", font=custom_font, background="light sky blue")
        self.label_height = ttk.Label(self, text="height:", font=custom_font3, background="light sky blue")
        self.entry_SizeH = ttk.Entry(self, width=7)
        self.label_width = ttk.Label(self, text="width:   ", font=custom_font3, background="light sky blue")
        self.label_SizeX = ttk.Label(self, text=" x ", font=custom_font, background="light sky blue")
        self.entry_SizeL = ttk.Entry(self, width=7)
        self.label_algorithem = ttk.Label(self, text="Algorithem:", font=custom_font, background="light sky blue")
        self.algorithm_combobox = ttk.Combobox(self, width=7)
        self.algorithm_combobox['values'] = ('', 'GA', 'PSO')
        self.choose_photo = ttk.Label(self, text="Choosing a structure:", font=custom_font, background="light sky blue")
        self.photo_combobox = ttk.Combobox(self, width=7)
        self.photo_combobox['values'] = ('', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13')
        self.run_button = ttk.Button(self, text="Run", command=self.switch_to_second_screen, style="Custom.TButton")
        self.Checkbutton = tk.Checkbutton(self, text="Image?", variable=self.check_image, onvalue=True, offvalue=False,
                                          background="light sky blue", font=custom_font3)

        self.label_Space.grid(row=1, column=0, padx=0, pady=40, sticky=tk.W)
        self.label_of_project.grid(row=2, column=0, padx=18, pady=30, sticky=tk.W)
        self.label_Following.grid(row=3, column=0, padx=20, pady=30, sticky=tk.W)
        self.label_Routers.grid(row=4, column=0, padx=20, pady=0, sticky=tk.W)
        self.entry_Routers.grid(row=4, column=1, padx=0, pady=10, sticky=tk.W)
        self.label_Clients.grid(row=5, column=0, padx=20, pady=20, sticky=tk.W)
        self.entry_Clients.grid(row=5, column=1, padx=0, pady=10, sticky=tk.W)
        self.label_Size.grid(row=6, column=0, padx=20, pady=0, sticky=tk.W)
        self.label_height.grid(row=6, column=1, padx=(0, 0), pady=0, sticky=tk.W)
        self.entry_SizeH.grid(row=6, column=2, padx=(0, 0), pady=0, sticky=tk.W)
        self.label_SizeX.grid(row=6, column=3, padx=0, pady=0, sticky=tk.W)
        self.label_width.grid(row=6, column=4, padx=0, pady=0, sticky=tk.W)
        self.entry_SizeL.grid(row=6, column=5, padx=0, pady=0, sticky=tk.W)
        self.label_algorithem.grid(row=7, column=0, padx=20, pady=15, sticky=tk.W)
        self.algorithm_combobox.grid(row=7, column=1, padx=0, pady=0)
        self.choose_photo.grid(row=8, column=0, padx=20, pady=0, sticky=tk.W)
        self.photo_combobox.grid(row=8, column=1, padx=20, pady=15, sticky=tk.W)
        self.Checkbutton.grid(row=8, column=2, padx=0, pady=0, sticky=tk.W)
        self.run_button.grid(row=9, columnspan=100, padx=400, pady=100)

    def switch_to_second_screen(self):
        routers = self.entry_Routers.get()
        clients = self.entry_Clients.get()
        height = self.entry_SizeH.get()
        width = self.entry_SizeL.get()
        algotype = self.algorithm_combobox.get()
        num_photo = self.photo_combobox.get()
        check_image = self.check_image.get()
        self.show_second_screen(routers, clients, height, width, algotype, num_photo, check_image)


class SecondScreen(tk.Frame):
    def __init__(self, parent, routers, clients, height, width, algotype, num_photo, check_image):
        super().__init__(parent)
        self.routers = routers
        self.clients = clients
        self.height = height
        self.width = width
        self.algotype = algotype
        self.num_photo = num_photo
        self.check_image = check_image
        self.second_screen = None
        self.iteration_number = tk.StringVar(value="Iteration number:         ")
        self.coverage_percentage = tk.StringVar(value="Coverage:            0%")
        if check_image:
            self.imageManager = ImageManager()
            self.imageManager.load_image(self.num_photo)
            self.imageManager.find_structure_shape()
            self.space = Area()
            self.space.generate_random_clients_for_photo(int(self.clients), self.imageManager.shape_polygon)
            self.algorithm = Algorithm(self.space, self.routers, self.space.clients, self, self.check_image,
                                       None, None, self.imageManager)
        else:
            self.space = Area(int(self.height), int(self.width))
            self.space.generate_random_clients(int(self.clients))
            self.algorithm = Algorithm(self.space, self.routers, self.space.clients, self, self.check_image,
                                       self.height, self.width, None)
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.is_paused = False

        self.tk_screen2 = tk.Toplevel()  # Create a new window (second screen)
        self.tk_screen2.title("WMNs Optimization - map")
        self.tk_screen2.configure(bg="light sky blue")
        style = ttk.Style()
        style.configure("Custom.TFrame", background="light sky blue")

        # Get screen width and height
        screen_width = self.tk_screen2.winfo_screenwidth()
        screen_height = self.tk_screen2.winfo_screenheight()

        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2

        # Set window size and position
        self.tk_screen2.geometry(f'1200x800+{x - 100}+{y - 120}')
        lable_font = ("Ariel", 20, "bold")
        custom_font = ("Ariel", 14)

        info_frame1 = ttk.Frame(self.tk_screen2, style="Custom.TFrame")
        info_frame1.pack(side=tk.TOP, anchor=tk.S, padx=80, pady=20)
        info_frame2 = ttk.Frame(self.tk_screen2, style="Custom.TFrame")
        info_frame2.pack(side=tk.TOP, anchor=tk.W, padx=20, pady=20)
        info_frame3 = ttk.Frame(self.tk_screen2, style="Custom.TFrame")
        info_frame3.pack(side=tk.BOTTOM, anchor=tk.S, padx=0, pady=10)
        self.top_label = ttk.Label(info_frame1, text="Optimization of routers placements in WMNs", font=lable_font,
                                   background="light sky blue")
        self.running_algorithm = ttk.Label(info_frame2, text="Running algorithm:", font=custom_font,
                                           background="light sky blue")
        self.name_algorithm = ttk.Label(info_frame2, text=self.algotype, font=custom_font, background="light sky blue")
        self.iteration_label = ttk.Label(info_frame2, textvariable=self.iteration_number, font=custom_font,
                                         background="light sky blue")
        self.coverage_label = ttk.Label(info_frame2, textvariable=self.coverage_percentage, font=custom_font,
                                        background="light sky blue")
        if self.check_image:
            self.details_label = ttk.Label(info_frame3, text=f"For {routers} routers, {clients} clients and"
                                                             f" image number {self.num_photo}", font=custom_font,
                                                             background="light sky blue")
        else:
            self.details_label = ttk.Label(info_frame3, text=f"For {routers} routers, {clients} clients and"
                                                             f" {height}X{width} area size", font=custom_font,
                                           background="light sky blue")
        self.stop_button = ttk.Button(info_frame3, text="Stop", command=self.stop_button, style="Custom.TButton")
        self.pause_continue_button = ttk.Button(info_frame3, text="Pause", command=self.toggle_pause_continue,
                                                style="Custom.TButton")

        self.top_label.grid(row=0, column=0, padx=0, pady=5)
        self.running_algorithm.grid(row=1, column=0, padx=0, pady=0, sticky=tk.W)
        self.name_algorithm.grid(row=1, column=0, padx=(170, 0), pady=0, sticky=tk.W)
        self.iteration_label.grid(row=2, column=0, padx=(0, 170), pady=5, sticky=tk.W)
        self.coverage_label.grid(row=3, column=0, padx=0, pady=0, sticky=tk.W)
        self.details_label.grid(row=1, column=1, padx=0, pady=20)
        self.stop_button.grid(row=2, column=1, padx=(200, 0), pady=0)
        self.pause_continue_button.grid(row=2, column=1, padx=(0, 200), pady=0)
        self.algorithm.run_algorithm(self.tk_screen2, algotype)

    def toggle_pause_continue(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_continue_button.config(text="Pause")
            self.algorithm.continue_button()
        else:
            self.is_paused = True
            self.pause_continue_button.config(text="Continue")
            self.algorithm.pause_button()

    def stop_button(self):
        self.tk_screen2.destroy()
        root = tk.Tk()
        OptimizationApp(root)


class OptimizationApp:
    def __init__(self, root):
        self.second_screen = None
        self.root = root
        self.root.title("WMNs Optimization")

        self.routers = None
        self.clients = None

        # Create an instance of the FirstScreen class and show it
        self.first_screen = FirstScreen(self.root, self.show_second_screen)
        self.first_screen.pack()

    def show_second_screen(self, routers, clients, height, width, algotype, num_photo, check_image):
        self.second_screen = SecondScreen(self.root, routers, clients, height, width, algotype, num_photo, check_image)
        self.second_screen.pack()
        self.root.withdraw()


def main():
    root = tk.Tk()
    OptimizationApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
