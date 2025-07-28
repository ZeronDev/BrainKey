import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

class EEGGraph(ctk.CTkFrame):
    def __init__(self):
        super().__init__()
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.line, _ = self.ax.plot([], [], "r-,")
        self.updateCanvas()
        self.canvas.get_tk_widget().pack(fill="both",expand=True)
    def updateCanvas(self):
        self.canvas.draw()
