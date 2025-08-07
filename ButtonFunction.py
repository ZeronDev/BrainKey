import Muse
import config
import threading
import customtkinter as ctk
from InputDialog import SelectInputDialog
from functools import partial
import csv
import Keyboard

def buttonGenerate(master, text, row, index, columnspan=1, full=False) -> ctk.CTkButton:
    button = ctk.CTkButton(master=master, text=text, font=("맑은 고딕", 20))
    print(columnspan)
    button.grid(row=row, column=index, padx=20, pady=10, sticky="nsew" if full else "ew", columnspan=columnspan)
    return button

def learn(): pass 
def run(): pass

buttons = []

def record(button):
    button.destroy()
    if not config.disabled and (config.other_screen == None or not config.other_screen.winfo_exists()):
        config.toggleAbility()
        recordingThread = threading.Thread(target=Muse.recordEEG, daemon=True)
        recordingThread.start()
        pauseButton = buttonGenerate(master=config.app, text="일시중지", row=3, index=0)
        pauseButton.configure(command=lambda: pause(pauseButton))
        terminateButton = buttonGenerate(master=config.app, text="종료", row=3, index=1)
        terminateButton.configure(command=terminate)
        buttons.append(pauseButton)
        buttons.append(terminateButton)
    else:
        config.other_screen.focus()
def pause(button): 
    if not Muse.isRecorded:
        return
    if Muse.pauseEvent.is_set():
        button.text = "일시중지"
        Muse.pauseEvent.clear()
    else:
        button.text = "재개"
        Muse.pauseEvent.set()#PAUSE event set할 것
def terminate(): 
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
        writer.writerows([ list(map(lambda data: data[x], Muse.BUFFER)) for x in range(5)])
    Muse.BUFFER = []
    config.other_screen = None
    Muse.terminateEvent.clear()
    for element in buttons:
        element.destroy()
    buttonGenerate(master=config.app, text="기록", row=3, index=0, columspan=2, full=True)
    config.toggleAbility()
    