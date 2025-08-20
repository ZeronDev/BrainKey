import Muse
import config
import threading
import numpy as np
import customtkinter as ctk
from InputDialog import SelectInputDialog
from functools import partial
import AiProcess
import csv
import DataManager
from Keyboard import pressKey

def buttonGenerate(master, text, row, index, columnspan=1, full=False) -> ctk.CTkButton:
    button = ctk.CTkButton(master=master, text=text, font=("맑은 고딕", 20))
    button.grid(row=row, column=index, padx=20, pady=10, sticky="nsew" if full else "ew", columnspan=columnspan)
    return button

def learn(): 
    if not config.disabled:
        config.toggleAbility()
        AiProcess.train()
        config.toggleAbility()
        config.app.progress.grid_forget()

isRunning = False

def prediction():
    global isRunning
    threshold = 0.5
    lock = threading.Lock()
    while isRunning:
        for x in DataManager.keybindWidget.elements:
            x[0].configure(fg_color="#292929")
        with lock:
             window = np.array(list(Muse.EEG_QUEUE.queue)[-256:])   # 마지막 256개 샘플만 추출
        window = window.T[..., np.newaxis]     
        window = np.expand_dims(window, axis=0) 
        y_pred = AiProcess.model.predict(window)

        if np.max(y_pred) > threshold:
            pred_class = np.argmax(y_pred)
            DataManager.keybindWidget.elements[pred_class][0].configure(fg_color="#206AA4")
            pressKey(pred_class)
    

def run(buttons): 
    global isRunning
    if not config.disabled:
        isRunning = True
        config.toggleAbility()
        runningThread = threading.Thread(target=prediction, daemon=True)
        runningThread.start()

        buttons[0].destroy()
        buttons[1].destroy()

        buttonGenerate(master=config.app, text="종료", row=1, index=0, columnspan=2)

def stopRunning(button):
    global isRunning
    isRunning = False
    button.destroy()

    learnButton = buttonGenerate(master=config.app, text="학습", row=1, index=0)
    learnButton.configure(command=learn)
    runButton = buttonGenerate(master=config.app, text="실행", row=1, index=1)
    runButton.configure(command=partial(run, (learnButton, runButton)))

buttons = []

def record(button):
    button.destroy()
    if not config.disabled and config.other_screen == None:
        config.toggleAbility()
        recordingThread = threading.Thread(target=Muse.recordEEG, daemon=True)
        recordingThread.start()
        pauseButton = buttonGenerate(master=config.app, text="일시중지", row=4, index=0)
        pauseButton.configure(command=lambda: pause(pauseButton))
        terminateButton = buttonGenerate(master=config.app, text="종료", row=4, index=1)
        terminateButton.configure(command=terminate)
        buttons.append(pauseButton)
        buttons.append(terminateButton)
    else:
        config.other_screen.focus()
def pause(button): 
    if not Muse.isRecorded:
        return
    if Muse.pauseEvent.is_set():
        button.configure(text="일시중지")
        Muse.pauseEvent.clear()
    else:
        button.configure(text="재개")
        Muse.pauseEvent.set()#PAUSE event set할 것
def terminate(): 
    if config.other_screen != None:
        return
    Muse.terminateEvent.set() #Terminate Event set할 것
    Muse.pauseEvent.clear()

    config.other_screen = SelectInputDialog("저장할 파일 선택")
    config.other_screen.focus()
    config.other_screen.grab_set()
    config.other_screen.wait_window()

    try:
        fileName = config.other_screen.getData().get()
        with open(config.path("data", fileName+".csv"), "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(Muse.BUFFER)
    except Exception as e: print("[terminate] 이미 파일이 열려있거나 예기치 못한 오류\n" + str(e))
    finally:
        Muse.BUFFER = []
        config.other_screen = None
        Muse.terminateEvent.clear()
        for element in buttons:
            element.destroy()
        recordButton = buttonGenerate(master=config.app, text="기록", row=4, index=0, columnspan=2, full=True)
        recordButton.configure(command=partial(record, recordButton))
        config.toggleAbility()
    