import tkinter as tk
from tkinter import ttk
from areaClass import Area
from algorithmClass import Algorithm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle

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
        self.second_screen = None

        self.fig, self.ax = plt.subplots(figsize=(4, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        # ax.clear()  # Clear the axis

        tk_screen2 = tk.Toplevel()  # Create a new window (second screen)
        tk_screen2.title("WMNs Optimization - map")
        tk_screen2.configure(bg="light sky blue")
        style = ttk.Style()
        style.configure("Custom.TFrame", background="light sky blue")

        # Get screen width and height
        screen_width = tk_screen2.winfo_screenwidth()
        screen_height = tk_screen2.winfo_screenheight()

        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2

        # Set window size and position
        tk_screen2.geometry(f'1000x700+{x + 100}+{y - 50}')
        lable_font = ("Ariel", 20, "bold")
        custom_font = ("Ariel", 14)

        info_frame1 = ttk.Frame(tk_screen2, style="Custom.TFrame")
        info_frame1.pack(side=tk.TOP, anchor=tk.S, padx=80, pady=20)
        info_frame2 = ttk.Frame(tk_screen2, style="Custom.TFrame")
        info_frame2.pack(side=tk.TOP, anchor=tk.W, padx=20, pady=20)
        info_frame3 = ttk.Frame(tk_screen2, style="Custom.TFrame")
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
        self.algorithm = Algorithm(self.space, self.routers, self.clients, self.height, self.height, self.second_screen)
        self.space.generate_random_clients(int(self.clients))
        self.algorithm.run_algorithm(tk_screen2, algotype, self.second_screen)

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
        self.second_screen = SecondScreen(self.root, routers, clients, height, width, algotype)
        self.second_screen.pack()

def main():
    root = tk.Tk()
    OptimizationApp(root)
    root.mainloop()

if __name__ == '__main__':
        main()
