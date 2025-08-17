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

muse = None
lslSartEvent = threading.Event()
pauseEvent = threading.Event()
terminateEvent = threading.Event()
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
    
    terminateEvent.wait()
    isRecorded = False

inlet = None
def receiving():
    global inlet, pauseEvent, terminateEvent, isRecorded
    sample, timestamp = inlet.pull_sample(1.5)
    if EEG_QUEUE.full():
        EEG_QUEUE.get()
    if not (pauseEvent.is_set() or terminateEvent.is_set()):
        EEG_QUEUE.put(sample)

    if isRecorded and not pauseEvent.is_set() and not terminateEvent.is_set():
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