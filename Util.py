import os
from keyboard import on_press, unhook_all
from functools import partial
import DataManager

def path(*args):
    return os.path.join(os.getcwd(), *args)
def onPress(event, bind):
    unhook_all()
    DataManager.keybindMap[bind] = event.name  

def listenKeyboard(bind):
    on_press(partial(onPress, bind))