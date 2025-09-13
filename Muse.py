from functools import partial
from muselsl import stream, list_muses, record
from pylsl import StreamInlet, resolve_streams
import threading
from config import path
import asyncio
import time
import config
import csv
from queue import Queue
import numpy as np
from InputDialog import SelectInputDialog

EEG_QUEUE = Queue(800) #큐
# EEG_DATA = Queue(256)
BUFFER = []

def clearQueue(queue: Queue):
    while not queue.empty():
        queue.get()

def terminate():
    global pauseEvent, BUFFER
    if config.other_screen != None:
        return
    pauseEvent.clear()

    config.other_screen = SelectInputDialog("저장할 파일 선택")
    config.other_screen.focus()
    config.other_screen.grab_set()
    config.other_screen.wait_window()

    try:
        fileName = config.other_screen.getData().get()
        with open(config.path("data", fileName+".csv"), "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(BUFFER)
    except Exception as e: print("[terminate] 이미 파일이 열려있거나 예기치 못한 오류\n" + str(e))
    finally:
        BUFFER = []
        config.other_screen = None
        config.pauseButton.destroy()
        recordButton = config.buttonGenerate(master=config.app, text="기록", row=4, index=0, columnspan=2, full=True)
        recordButton.configure(command=partial(record, recordButton))
        config.toggleAbility()

muse = None
lslSartEvent = threading.Event()
pauseEvent = threading.Event()
isRecorded = False

def streaming(): #MUSELSL 송신
    global muse, lslSartEvent
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        muse = list_muses()[0]
        lslSartEvent.set()
        stream(muse['address'])
    except Exception as e:
        print("MUSE 연결 안됨")
        # print(f"[ERR] Muse Streaming Error Occurred \n{e}")
        # print(e)


def recordEEG():
    global terminateEvent, pauseEvent, BUFFER, isRecorded
    clearQueue(EEG_QUEUE)
    isRecorded = True
    progressBar = config.TimerProgressBar(terminate, 30)
    progressBar.start()
    isRecorded = False

inlet = None
def receiving():
    global inlet, pauseEvent,isRecorded
    sample, timestamp = inlet.pull_sample(1.5)
    if EEG_QUEUE.full():
        EEG_QUEUE.get()
    if isRecorded and not pauseEvent.is_set():
        EEG_QUEUE.put(sample)

    if isRecorded and not pauseEvent.is_set():
        BUFFER.append([ float(data) for data in sample ])
    # print(EEG_QUEUE.get())

def pylslrecv(): #PYLSL 수신
    global inlet, lslSartEvent
    lslSartEvent.wait()

    try:
        lsl = resolve_streams(5.0)
        inlet = StreamInlet(lsl[0])

        while True:
            receiving()
            #time.sleep(0.1)
    except Exception as e:
        print(f"[ERR] Muse Receiving Error Occurred \n{e}")
        
sendingThread = threading.Thread(target=streaming, daemon=True)
sendingThread.start()

receivingThread = threading.Thread(target=pylslrecv, daemon=True)
receivingThread.start()
#TODO