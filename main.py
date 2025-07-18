import customtkinter as ctk
from KeySelector import KeySelector
from functools import partial
import pickle

from Util import path

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("600x800")
        self.wm_minsize(600, 800)
        self.title("브레인 키")
        self.grid_rowconfigure((0,2), weight=15)
        self.grid_rowconfigure((1,3), weight=1)
        self.grid_columnconfigure((0,1), weight=1)
        # self.protocol("WM_DELETE_WINDOW", partial(stopObserver, self))
        keySelector = KeySelector(self)
        keySelector.grid(row=0, column=0, sticky="nsew", columnspan=2, padx=20, pady=10)

        learning = ctk.CTkButton(master=self, text="학습", font=("맑은 고딕", 20))
        learning.grid(row=1, column=0, padx=(20, 5), pady=5, sticky="nsew")
        running = ctk.CTkButton(master=self, text="실행", font=("맑은 고딕", 20))
        running.grid(row=1, column=1, padx=(5, 20), pady=5, sticky="nsew")


        recording = ctk.CTkButton(master=self, text="기록", font=("맑은 고딕", 20))
        recording.grid(row=3, column=0, padx=20, pady=10, sticky="nsew", columnspan=2)

    def onExit(self):
        # with open(path("data","keybind.pickle"), "wb") as file:
        #     pickle.dump({}, file)
        # stopObserver(self)
        pass

ctk.set_default_color_theme("dark-blue")
ctk.set_appearance_mode("Dark")

app = App()
app.mainloop()