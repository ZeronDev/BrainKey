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

        config.buttonGenerate(master=config.app, text="종료", row=1, index=0, columnspan=2)

def stopRunning(button):
    global isRunning
    isRunning = False
    button.destroy()

    learnButton = config.buttonGenerate(master=config.app, text="학습", row=1, index=0)
    learnButton.configure(command=learn)
    runButton = config.buttonGenerate(master=config.app, text="실행", row=1, index=1)
    runButton.configure(command=partial(run, (learnButton, runButton)))


def record(button):
    button.destroy()
    if not config.disabled and config.other_screen == None:
        config.toggleAbility()
        recordingThread = threading.Thread(target=Muse.recordEEG, daemon=True)
        recordingThread.start()
        pauseButton = config.buttonGenerate(master=config.app, text="일시중지", row=4, index=0)
        pauseButton.configure(command=lambda: pause(pauseButton))
        config.pauseButton = pauseButton
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
