from muselsl import stream, list_muses, record
from pylsl import StreamInlet, resolve_streams
import threading
from config import path
import asyncio
import time
from queue import Queue

EEG_QUEUE = Queue(600) #큐

def recordEEG(name):
    record(duration=60, filename=path("data",name))
muse = None
lslSartEvent = threading.Event()

def streaming(): #MUSELSL 송신
    global muse, lslSartEvent
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    muse = list_muses()[0]
    try:
        lslSartEvent.set()
        stream(muse['address'])
    except Exception as e:
        print(f"[ERR] Muse Streaming Error Occurred \n{e}")
        print(e)
inlet = None
def receiving():
    global inlet
    sample, timestamp = inlet.pull_sample(1.5)
    if EEG_QUEUE.full():
        EEG_QUEUE.get()
    else:
        EEG_QUEUE.put(sample)
    # print(EEG_QUEUE.get())

def pylslrecv(): #PYLSL 수신
    global inlet, lslSartEvent
    lslSartEvent.wait()

    try:
        lsl = resolve_streams(5.0)
        inlet = StreamInlet(lsl[0])

        while True:
            receiving()
            time.sleep(0.1)
    except Exception as e:
        print(f"[ERR] Muse Receiving Error Occurred \n{e}")
        
# sendingThread = threading.Thread(target=streaming, daemon=True)
# sendingThread.start()

# receivingThread = threading.Thread(target=pylslrecv, daemon=True)
# receivingThread.start()
#TODO