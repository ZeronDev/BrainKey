import os
# from keyboard import on_press, unhook_all
import DataManager
import Keybind

app = None

def onPress(event, bind, index):
    global app
    DataManager.keybindMap[bind][index] = event.keysym.upper()
    DataManager.keybindWidget.refresh()
    Keybind.clickedButton = ""
    app.unbind("<KeyPress>")
def listenKeyboard(bind, index):
    global app
    app.unbind("<KeyPress>")
    app.bind("<KeyPress>", lambda event: onPress(event, bind, index))