import os
import watchdog.events
import watchdog
from Util import path
import pickle
import watchdog.observers
def reload(): return list(map(lambda fileName: os.path.splitext(fileName)[0],os.listdir(path("data"))))
eegData = reload()

# if "keybind.pickle" in eegData: eegData.remove("keybind.pickle")
keybindWidget = None
keybindMap = {}

# try:
#     with open(path("data","keybind.pickle"), "rb") as file:
#         keybindMap = pickle.load(file)
# except FileNotFoundError:
#     with open(path("data","keybind.pickle"), "wb") as file:
#         for data in eegData:
#             keybindMap[data] = []
#         pickle.dump(keybindMap, file)

# class FileHandler(watchdog.events.FileSystemEventHandler):
#     def __init__(self):
#         super()
#     def on_created(self, event):
#         if event.is_directory: return
#         eegData.append(os.path.basename(event.src_path)) #추후 파일 자료형으로 저장할 것
#         keybindWidget.refresh()
#     def on_deleted(self, event):
#         if event.is_directory: return
#         eegData.remove(os.path.basename(event.src_path))
#         keybindWidget.refresh()
#     def on_moved(self, event):
#         eegData[eegData.index(event.src_path)] = event.dest_path
#         if event.is_directory: return
# observer = watchdog.observers.Observer()
# observer.schedule(FileHandler(), path("data"), recursive=False)
# observer.start()

# def stopObserver(app):
#     global observer
#     observer.stop()
#     observer.join()
#     app.destroy()
    
