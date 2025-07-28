from muselsl import stream, list_muses, record
from pylsl import StreamInlet, resolve_streams
import threading
from Util import path

def recordEEG(name):
    record(duration=60, filename=path("data",name))
muse = None

lsl = resolve_streams('type', 'EEG')
inlet = StreamInlet(lsl[0])

def streaming():
    global muse
    muse = list_muses()[0]
    try:
        stream(muse['address'])
    except:
        print("[ERR] Muse Connection Error Occurred")
def receiving():
    global inlet
    sample, timestamp = inlet.pull_sample(1.5)
    if not sample: return sample

streaming()
sendingThread = threading.Thread(target=streaming, daemon=True)
sendingThread.start()

