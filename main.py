import threading
import time
import tkinter
import tkinter as tk
from tkinter import ttk, messagebox
from PSO_Class import PSO
from area_Class import Area
from GA_Class import GA
from image_Class import ImageManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from client_Class import Client
from PIL import Image, ImageTk


class FirstScreen(tk.Frame):
    def __init__(self, root, show_second_screen):
        super().__init__(root)
        self.option_manual = None
        self.option_random = None
        self.image_display_label = None
        self.imageManager = None
        self.entry_SizeL = None
        self.entry_SizeH = None
        self.photo_combobox = None
        self.clients = []
        self.show_second_screen = show_second_screen
        self.root = root
        screen_height = self.master.winfo_screenheight()
        screen_width = self.master.winfo_screenwidth()
        self.check_image = tk.IntVar()
        self.random_position_clients = tk.IntVar()

        style = ttk.Style()
        style.configure("Custom.TFrame", background="light sky blue")
        info_frame1 = ttk.Frame(self.root, style="Custom.TFrame")
        info_frame1.pack(side=tk.TOP, anchor=tk.S, padx=80, pady=0)
        self.root.configure(bg="light sky blue")

        self.custom_font = ("Ariel", 16)
        self.custom_font2 = ("Ariel", 22, "bold")
        self.custom_font3 = ("Ariel", 12)
        self.custom_font4 = ("Ariel", 16, "bold")

        style.configure("Custom.TButton", font=self.custom_font, background="light sky blue")
        style.configure("Checkbutton", font=self.custom_font, background="light sky blue")
        self.configure(bg="light sky blue")

        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2

        self.master.geometry(f'1050x750+{x - 100}+{y - 70}')

        self.label_Space = ttk.Label(info_frame1, text=" ", background="light sky blue")
        self.label_of_project = ttk.Label(info_frame1, text="Optimization of routers placements in WMNs",
                                          font=self.custom_font2,
                                          background="light sky blue")
        self.label_Following = ttk.Label(self, text="Please insert the following:", font=self.custom_font4,
                                         background="light sky blue")
        self.label_Routers = ttk.Label(self, text="Number of routers:", font=self.custom_font,
                                       background="light sky blue")
        self.entry_Routers = ttk.Entry(self, width=7)
        self.label_Clients = ttk.Label(self, text="Numer of clients:", font=self.custom_font,
                                       background="light sky blue")
        self.entry_Clients = ttk.Entry(self, width=7)
        self.label_algorithem = ttk.Label(self, text="Algorithem:", font=self.custom_font, background="light sky blue")
        self.algorithm_combobox = ttk.Combobox(self, width=7)
        self.algorithm_combobox['values'] = ('GA', 'PSO')
        self.label_method = ttk.Label(self, text="Calculation method:", font=self.custom_font,
                                      background="light sky blue")
        self.run_button = ttk.Button(self, text="Run", command=self.switch_to_second_screen, style="Custom.TButton")
        self.option_Rect = tk.Radiobutton(self, text="Rectangle", variable=self.check_image, value=2,
                                          command=self.show_buttons, background="light sky blue",
                                          font=self.custom_font3)
        self.option_Image = tk.Radiobutton(self, text="Image", variable=self.check_image, value=1,
                                           command=self.show_buttons, background="light sky blue",
                                           font=self.custom_font3)

        self.label_Space.grid(row=1, column=0, padx=0, pady=10, sticky=tk.W)
        self.label_of_project.grid(row=2, column=0, padx=18, pady=45)
        self.label_Following.grid(row=3, column=0, padx=15, pady=30, sticky=tk.W)
        self.label_Routers.grid(row=4, column=0, padx=20, pady=0, sticky=tk.W)
        self.entry_Routers.grid(row=4, column=1, padx=0, pady=15, sticky=tk.E)
        self.label_Clients.grid(row=5, column=0, padx=20, pady=0, sticky=tk.W)
        self.entry_Clients.grid(row=5, column=1, padx=0, pady=0, sticky=tk.E)
        self.label_algorithem.grid(row=6, column=0, padx=20, pady=10, sticky=tk.W)
        self.algorithm_combobox.grid(row=6, column=1, padx=0, pady=0, sticky=tk.E)
        self.label_method.grid(row=7, column=0, padx=20, pady=0, sticky=tk.W)
        self.option_Rect.grid(row=7, column=1, padx=0, pady=0, sticky=tk.E)
        self.option_Image.grid(row=7, column=2, padx=0, pady=0, sticky=tk.W)
        self.run_button.grid(row=10, columnspan=100, padx=400, pady=184, sticky=tk.W)

    def update_screen_display(self, event=None):
        if self.check_image.get() == 1:
            selected_number = self.photo_combobox.get()
            if selected_number:
                image_number = int(selected_number)
                selected_image = self.imageManager.preloaded_images[image_number][1]
                image_width = selected_image.width()
                image_height = selected_image.height()
                self.image_display_label.config(width=image_width, height=image_height)
                if hasattr(self, "image_item"):
                    self.image_display_label.itemconfig(self.image_item, image=selected_image)
                else:
                    self.image_item = self.image_display_label.create_image(0, 0, image=selected_image, anchor=tk.NW)
                self.image_display_label.image = selected_image
        else:
            canvas_width = int(self.entry_SizeH.get()) if self.entry_SizeH.get() else 0
            canvas_height = int(self.entry_SizeL.get()) if self.entry_SizeL.get() else 0
            if canvas_width > 0 and canvas_height > 0:
                self.image_display_label.config(width=canvas_height, height=canvas_width)
                smooth_image = Image.new("RGB", (0, 0), color="white")
                smooth_photo = ImageTk.PhotoImage(smooth_image)
                self.image_item = self.image_display_label.create_image(250, 0, image=smooth_photo, anchor=tk.NW)

    def show_buttons(self):
        for row in range(8, 11):
            for widget in self.grid_slaves(row=row):
                widget.grid_forget()

        if self.check_image.get() == 1:
            choose_photo = ttk.Label(self, text="Structure: \n\nDistribution clients:", font=self.custom_font,
                                     background="light sky blue")
            self.photo_combobox = ttk.Combobox(self, width=7)
            if self.imageManager == None:
                self.imageManager = ImageManager()
                self.imageManager.preload_images(1, 13)
            self.photo_combobox['values'] = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13')
            choose_photo.grid(row=8, column=0, padx=20, pady=5, sticky=tk.NW)
            self.photo_combobox.grid(row=8, column=1, padx=0, pady=20, sticky=tk.N)
            self.photo_combobox.bind("<<ComboboxSelected>>", self.update_screen_display)
            self.photo_combobox.set('1')
            self.image_display_label = tk.Canvas(self)
            self.image_display_label.grid(row=8, column=4, padx=10, pady=(5, 10), sticky=tk.N)
            self.random_position_clients.set(2)
            self.option_random = tk.Radiobutton(self, text="Random", variable=self.random_position_clients, value=2,
                                                background="light sky blue", font=self.custom_font3)
            self.option_manual = tk.Radiobutton(self, text="Manual", variable=self.random_position_clients,
                                                value=1, background="light sky blue", font=self.custom_font3)
            self.option_random.grid(row=8, column=1, padx=0, pady=(70, 80), sticky=tk.NW)
            self.option_manual.grid(row=8, column=1, padx=0, pady=(110, 0), sticky=tk.NW)
            self.random_position_clients.trace_add('write', self.bind_click_event)
            self.update_screen_display(self.check_image.get())
            self.run_button.grid(row=11, columnspan=100, padx=400, pady=20)
        elif self.check_image.get() == 2:
            label_Size = ttk.Label(self, text="Size of area:\n\nDistribution clients:", font=self.custom_font,
                                   background="light sky blue")
            label_height = ttk.Label(self, text="Height:\n     x\nWidth:       ", font=self.custom_font3,
                                     background="light sky blue")
            self.random_position_clients.set(2)
            self.option_random = tk.Radiobutton(self, text="Random", variable=self.random_position_clients, value=2,
                                                background="light sky blue", font=self.custom_font3)
            self.option_manual = tk.Radiobutton(self, text="Manual", variable=self.random_position_clients,
                                                value=1, command=self.update_screen_display,
                                                background="light sky blue", font=self.custom_font3)
            self.entry_SizeH = ttk.Entry(self, width=7)
            self.entry_SizeL = ttk.Entry(self, width=7)
            label_Size.grid(row=8, column=0, padx=20, pady=5, sticky=tk.NW)
            label_height.grid(row=8, column=1, padx=0, pady=0, sticky=tk.NE)
            self.entry_SizeH.grid(row=8, column=2, padx=(0, 0), pady=10, sticky=tk.NW)
            self.entry_SizeL.grid(row=8, column=2, padx=0, pady=40, sticky=tk.NW)
            self.option_random.grid(row=8, column=1, padx=0, pady=0, sticky=tk.SW)
            self.option_manual.grid(row=8, column=2, padx=0, pady=0, sticky=tk.SW)
            height = int(self.entry_SizeH.get()) if self.entry_SizeH.get() else 0
            width = int(self.entry_SizeL.get()) if self.entry_SizeL.get() else 0
            self.image_display_label = tk.Canvas(self, width=width, height=height)
            self.image_display_label.grid(row=8, column=4, padx=10, pady=(5, 10), sticky=tk.N)
            self.random_position_clients.trace_add('write', self.bind_click_event)
            self.update_screen_display(self.check_image.get())
            self.run_button.grid(row=10, columnspan=100, padx=400, pady=20)

    def handle_click(self, event):
        scaleX = 4.85
        scaleY = 2.9
        x = event.x
        y = event.y
        if self.check_image.get() == 2:  # User coordinate
            scaleX = 1
            scaleY = 1
            y = int(self.entry_SizeH.get()) - event.y

        if len(self.clients) >= int(self.entry_Clients.get()):
            messagebox.showwarning("Warning", "Maximum number of clients reached.")
            return
        client = Client(x * scaleX, y * scaleY)
        self.clients.append(client)
        self.draw_client_locations(self.image_display_label, self.clients)

    def draw_client_locations(self, canvas, clients):
        scaleX = 1
        scaleY = 1
        if self.check_image.get() == 1:
            scaleX = 4.85
            scaleY = 2.9

        canvas.delete("clients")
        x_size = 5
        line_width = 2
        for client in clients:
            if self.check_image.get() == 1:
                x, y = (client.x / scaleX), (client.y / scaleY)
            else:
                x, y = (client.x / scaleX), (int(self.entry_SizeH.get()) - client.y / scaleY)
            canvas.create_line(x - x_size, y - x_size, x + x_size, y + x_size, fill="black", width=line_width,
                               tags="clients")
            canvas.create_line(x - x_size, y + x_size, x + x_size, y - x_size, fill="black", width=line_width,
                               tags="clients")

    def bind_click_event(self, *args):
        if self.random_position_clients.get() == 1:
            self.image_display_label.bind("<Button-1>", self.handle_click)
        else:
            self.image_display_label.unbind("<Button-1>")

    def switch_to_second_screen(self):
        routers = self.entry_Routers.get()
        if self.random_position_clients.get() == 2:
            clients = self.entry_Clients.get()
        else:
            clients = self.clients
        algotype = self.algorithm_combobox.get()
        check_image = self.check_image.get()

        if check_image == 2:
            height = self.entry_SizeH.get()
            width = self.entry_SizeL.get()
            self.show_second_screen(routers, clients, height, width, algotype, None, 0, self.random_position_clients)
        else:
            num_photo = self.photo_combobox.get()
            self.show_second_screen(routers, clients, None, None, algotype, num_photo, 1, self.random_position_clients)


class SecondScreen(tk.Frame):
    def __init__(self, root, first_screen, routers, clients, height, width, algotype, num_photo, check_image
                 , random_position_clients):
        super().__init__(root)
        self.root = root
        self.first_screen = first_screen
        self.routers = routers
        self.clients = clients
        self.radius = int(5)
        self.height = height
        self.width = width
        self.algotype = algotype
        self.num_photo = num_photo
        self.check_image = check_image
        self.random_position_clients = random_position_clients
        self.second_screen = None
        self.iteration_number = tk.StringVar(value="Iteration number:         ")
        self.coverage_percentage = tk.StringVar(value="Coverage:            0%")
        self.SGC_text = tk.StringVar(value="Giant component size:          ")
        self.fitness_text = tk.StringVar(value="Fitness score:               ")
        start_time = time.time()
        elapsed_time = time.time() - start_time
        self.speed_var = 0
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        self.time_text = tk.StringVar(value="Time:     " + formatted_time)

        self.tk_screen2 = tk.Toplevel()
        self.tk_screen2.title("WMNs Optimization - map")
        self.tk_screen2.configure(bg="light sky blue")
        style = ttk.Style()
        style.configure("Custom.TFrame", background="light sky blue")
        style.configure("Horizontal.TScale", background="light sky blue")

        screen_width = self.tk_screen2.winfo_screenwidth()
        screen_height = self.tk_screen2.winfo_screenheight()

        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2

        self.tk_screen2.geometry(f'1200x750+{x - 200}+{y - 65}')
        lable_font = ("Ariel", 22, "bold")
        custom_font = ("Ariel", 14)

        info_frame1 = ttk.Frame(self.tk_screen2, style="Custom.TFrame")
        info_frame1.pack(side=tk.TOP, anchor=tk.S, padx=80, pady=20)
        info_frame2 = ttk.Frame(self.tk_screen2, style="Custom.TFrame")
        info_frame2.pack(side=tk.TOP, anchor=tk.W, padx=20, pady=20)
        info_frame3 = ttk.Frame(self.tk_screen2, style="Custom.TFrame")
        info_frame3.pack(side=tk.BOTTOM, anchor=tk.S, padx=0, pady=10)
        self.sgc_label = ttk.Label(info_frame2, textvariable=self.SGC_text, font=custom_font,
                                   background="light sky blue")
        self.fitness_label = ttk.Label(info_frame2, textvariable=self.fitness_text, font=custom_font,
                                       background="light sky blue")
        self.time_label = ttk.Label(info_frame2, textvariable=self.time_text, font=custom_font,
                                    background="light sky blue")
        self.sgc_label.grid(row=2, column=1, padx=0, pady=0, sticky=tk.W)
        self.fitness_label.grid(row=3, column=1, padx=(0, 20), pady=0, sticky=tk.W)
        self.time_label.grid(row=2, column=2, padx=50, pady=0, sticky=tk.W)

        if algotype == 'PSO':
            self.label_number_of_particle = ttk.Label(info_frame2, text="Number of particle:", font=custom_font,
                                                      background="light sky blue")
            self.label_number_of_particle.grid(row=1, column=1, padx=0, pady=0, sticky=tk.W)
            self.number_of_particle = ttk.Combobox(info_frame2, width=8)
            self.number_of_particle['values'] = ('Graph', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'
                                                 , '13', '14', '15', '16', '17', '18', '19', '20')
            self.number_of_particle.set('1')

        if check_image:
            self.imageManager = ImageManager()
            self.imageManager.load_image(self.num_photo)
            self.imageManager.find_structure_shape()
            self.space = Area()
            if self.random_position_clients.get() == 2:
                self.space.generate_random_clients_for_photo(int(self.clients), self.imageManager.shape_polygon)
            else:
                self.space.clients = self.clients
            if algotype == 'GA':
                self.algorithm_GA = GA(self.space, self, None, None, self.imageManager)
            else:
                self.algorithm_PSO = PSO(self.space, self, None, None, self.imageManager)
        else:
            self.space = Area(int(self.height), int(self.width))
            if self.random_position_clients.get() == 2:
                self.space.generate_random_clients(int(self.clients))
            else:
                self.space.clients = self.clients
            if algotype == 'GA':
                self.algorithm_GA = GA(self.space, self, self.height, self.width, None)
            else:
                self.algorithm_PSO = PSO(self.space, self, int(self.height), int(self.width), None)
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.is_paused = False

        self.top_label = ttk.Label(info_frame1, text="Optimization of routers placements in WMNs", font=lable_font,
                                   background="light sky blue")
        self.running_algorithm = ttk.Label(info_frame2, text="Running algorithm:", font=custom_font,
                                           background="light sky blue")
        self.name_algorithm = ttk.Label(info_frame2, text=self.algotype, font=custom_font, background="light sky blue")
        self.iteration_label = ttk.Label(info_frame2, textvariable=self.iteration_number, font=custom_font,
                                         background="light sky blue")
        self.coverage_label = ttk.Label(info_frame2, textvariable=self.coverage_percentage, font=custom_font,
                                        background="light sky blue")
        self.speed_label = ttk.Label(info_frame2, text="Speed:", font=custom_font, background="light sky blue")
        self.speed_var = tkinter.IntVar()
        self.speed_slider = ttk.Scale(info_frame2, from_=0, to=300, orient="horizontal", variable=self.speed_var,
                                      length=150, style="Horizontal.TScale")
        if self.check_image:
            if self.random_position_clients.get() == 2:
                self.details_label = ttk.Label(info_frame3, text=f"For {routers} routers, {clients} clients and"
                                                                 f" image number {self.num_photo}", font=custom_font,
                                               background="light sky blue")
            else:
                self.details_label = ttk.Label(info_frame3, text=f"For {routers} routers, {len(clients)} clients and"
                                                                 f" image number {self.num_photo}", font=custom_font,
                                               background="light sky blue")
        else:
            if self.random_position_clients.get() == 2:
                self.details_label = ttk.Label(info_frame3, text=f"For {routers} routers, {clients} clients and an area"
                                                                 f" of {height}X{width}", font=custom_font,
                                               background="light sky blue")
            else:
                self.details_label = ttk.Label(info_frame3, text=f"For {routers} routers, {len(clients)} "
                                                                 f"clients and an area of {height}X{width}"
                                               , font=custom_font, background="light sky blue")

        self.stop_button = ttk.Button(info_frame3, text="Stop", command=self.stop_button, style="Custom.TButton")
        self.pause_continue_button = ttk.Button(info_frame3, text="Pause", command=self.toggle_pause_continue,
                                                style="Custom.TButton")

        self.top_label.grid(row=0, column=0, padx=0, pady=5)
        self.running_algorithm.grid(row=1, column=0, padx=0, pady=0, sticky=tk.W)
        self.name_algorithm.grid(row=1, column=0, padx=(170, 0), pady=0, sticky=tk.W)
        self.iteration_label.grid(row=2, column=0, padx=(0, 100), pady=5, sticky=tk.W)
        if algotype == 'PSO':
            self.number_of_particle.grid(row=1, column=1, padx=(200, 0), pady=0, sticky=tk.W)
        self.coverage_label.grid(row=3, column=0, padx=0, pady=0, sticky=tk.W)
        self.speed_label.grid(row=3, column=2, padx=50, pady=0, sticky=tk.W)
        self.speed_slider.grid(row=3, column=2, padx=130, pady=0, sticky=tk.W)
        self.details_label.grid(row=1, column=1, padx=0, pady=20)
        self.stop_button.grid(row=2, column=1, padx=(200, 0), pady=0)
        self.pause_continue_button.grid(row=2, column=1, padx=(0, 200), pady=0)

        if algotype == 'GA':
            self.thread = threading.Thread(target=self.algorithm_GA.GA_algorithm, args=(self.tk_screen2, 1000000))
            self.thread.start()
        elif algotype == 'PSO':
            self.thread = threading.Thread(target=self.algorithm_PSO.PSO_algorithm, args=(self.tk_screen2, 1000000))
            self.thread.start()
        else:
            raise ValueError("Invalid algorithm type")

    def toggle_pause_continue(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_continue_button.config(text="Pause")
            if self.algotype == 'GA':
                self.algorithm_GA.continue_button()
            else:
                self.algorithm_PSO.continue_button()
        else:
            self.is_paused = True
            self.pause_continue_button.config(text="Continue")
            if self.algotype == 'GA':
                self.algorithm_GA.pause_button()
            else:
                self.algorithm_PSO.pause_button()

    def stop_button(self):
        self.tk_screen2.destroy()
        self.root.deiconify()
        self.first_screen.show_buttons()
        self.first_screen.run_button.grid(row=11, columnspan=100, padx=400, pady=150, sticky=tk.W)
        self.root.mainloop()


class OptimizationApp:
    def __init__(self, root):
        self.second_screen = None
        self.root = root
        self.root.title("WMNs Optimization")
        self.routers = None
        self.clients = None
        self.first_screen = FirstScreen(self.root, self.show_second_screen)
        self.first_screen.pack()

    def show_second_screen(self, routers, clients, height, width, algotype, num_photo, check_image
                           , random_position_clients):
        if not check_image:
            self.first_screen.entry_SizeH.delete(0, tk.END)
            self.first_screen.entry_SizeL.delete(0, tk.END)
        else:
            self.first_screen.photo_combobox.set(' ')
        self.first_screen.entry_Routers.delete(0, tk.END)
        self.first_screen.entry_Clients.delete(0, tk.END)
        self.first_screen.algorithm_combobox.set(' ')
        self.first_screen.check_image.set(False)
        self.first_screen.option_Rect = tk.Radiobutton(self.root, text="Rectangle",
                                                       variable=self.first_screen.check_image, value=0,
                                                       command=self.first_screen.show_buttons,
                                                       background="light sky blue", font=self.first_screen.custom_font3)
        self.first_screen.option_Image = tk.Radiobutton(self.root, text="Image", variable=self.first_screen.check_image,
                                                        value=1, command=self.first_screen.show_buttons,
                                                        background="light sky blue",
                                                        font=self.first_screen.custom_font3)

        self.second_screen = SecondScreen(self.root, self.first_screen, routers, clients, height,
                                          width, algotype, num_photo, check_image, random_position_clients)
        self.second_screen.pack()
        self.root.withdraw()


def main():
    root = tk.Tk()
    OptimizationApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
