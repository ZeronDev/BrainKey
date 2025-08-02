import Muse
import config
import threading
import customtkinter as ctk
from InputDialog import SelectInputDialog
from functools import partial
import csv
import Keyboard

def buttonGenerate(master, text, index, fun, recording=False) -> ctk.CTkButton:
    button = ctk.CTkButton(master=master, text=text, font=("맑은 고딕", 20))
    button.grid(row=3, column=index, padx=20, pady=10, sticky="nsew", columnspan=2 if recording else 1)
    return button

def learn(): pass 
def run(): pass

buttons = []

def record(event):
    if not config.disabled and (config.other_screen == None or not config.other_screen.winfo_exists()):
        config.toggleAbility()
        recordingThread = threading.Thread(target=Muse.recordEEG, daemon=True)
        recordingThread.start()
        pauseButton = buttonGenerate(config.app, "일시중지", 0)
        pauseButton.bind(sequence="<Button-1>", command=lambda: pause(pauseButton))
        terminateButton = buttonGenerate(config.app, "종료", 1)
        terminateButton.bind(sequence="<Button-1>", command=terminate)
        buttons.append(pauseButton)
        buttons.append(terminateButton)
    else:
        config.other_screen.focus()
def pause(event, button): 
    if not Muse.isRecorded:
        return
    if Muse.pauseEvent.is_set():
        button.text = "일시중지"
        Muse.pauseEvent.clear()
    else:
        button.text = "재개"
        Muse.pauseEvent.set()#PAUSE event set할 것
def terminate(event): 
    if (config.other_screen != None or config.other_screen.winfo_exists()):
        return
    Muse.terminateEvent.set() #Terminate Event set할 것
    Muse.pauseEvent.clear()

    config.other_screen = SelectInputDialog("저장할 파일 선택")
    config.other_screen.focus()
    config.other_screen.grab_set()
    config.other_screen.wait_window()

    fileName = config.other_screen.getData()
    with open(config.path("data", fileName+".csv"), "w") as file:
        writer = csv.writer(file)
        writer.writerows(Muse.BUFFER)
    Muse.BUFFER = []
    config.other_screen = None
    Muse.terminateEvent.clear()
    for element in buttons:
        element.destroy()
    buttonGenerate(config.app, "기록", 0, record, True)
    config.toggleAbility()
    