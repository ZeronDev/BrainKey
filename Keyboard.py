import os
# from keyboard import on_press, unhook_all
import DataManager
import Keybind
import config

def onPress(event, bind, index):
    DataManager.keybindMap[bind][index] = event.keysym.upper()
    DataManager.keybindWidget.refresh()
    Keybind.clickedButton = ""
    config.app.unbind("<KeyPress>")
def listenKeyboard(bind, index):
    config.app.unbind("<KeyPress>")
    config.app.bind("<KeyPress>", lambda event: onPress(event, bind, index))