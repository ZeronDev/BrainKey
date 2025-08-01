import Muse
import config
import threading
from InputDialog import SelectInputDialog

def learn(): pass 
def run(): pass
def record():
    if not config.disabledand and (config.other_screen == None or not config.other_screen.winfo_exists()):
        config.toggleAbility()
        recordingThread = threading.Thread(target=Muse.recordEEG, daemon=True)
        recordingThread.start()
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
    Muse.terminateEvent.set() #Terminate Event set할 것
    
    config.toggleAbility()
    config.other_screen = SelectInputDialog("저장할 파일 선택")
    config.other_screen.focus()
    config.other_screen.grab_set()
    config.other_screen.wait_window()

    fileName = config.other_screen.getData()
    config.other_screen = None