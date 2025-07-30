import customtkinter as ctk
import os
from config import path
from DataManager import eegData, keybindMap, reload
import uuid
from PIL import Image
import Keyboard

buttonList = []
addImage = ctk.CTkImage(dark_image=Image.open(path("images", "add.png")), size=(22, 22))
class KeybindSelector(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master=master,fg_color="transparent")
        self.elements = []
        # self.buttonList = []
        self.listElement()
        
         #UUID 저장

    def refresh(self):
        global buttonList
        for element in self.elements:
            element.destroy()
        for keymap in sum(buttonList, []):
            if keymap.winfo_exists(): 
                keymap.destroy()
        eegData.clear()
        eegData.extend(reload())
        self.elements.clear()
        buttonList.clear()
        self.listElement()
        
    def listElement(self):
        global buttonList
        for index, file in enumerate(eegData):
            keylabel = ctk.CTkButton(master=self, text=file, font=("맑은 고딕", 20), width=130, fg_color="#292929", corner_radius=7, hover=False, anchor="center",)# border_width=0.5, border_color="#d4d4d4")
            keylabel.grid(row=index, column=0, pady=6, padx=(10, 4), sticky="w")
            columnCounter = 1
            _buttonList = []
            for keymap in keybindMap.get(file, []):
                keymapButton = KeyButton(self, file, keymap)
                keymapButton.grid(row=index, column=columnCounter, pady=6, padx=2)
                columnCounter += 1
                _buttonList.append(keymapButton)
            buttonList.append(_buttonList)
            # keymap = ctk.CTkSegmentedButton(master=self, values=keybindMap.get(file, []), fg_color="#212121", selected_color="#206AA4", unselected_color="#1D1E1E", text_color="#ffffff")
            # keymap.grid(row=index, column=1, pady=5, padx=3)
            # for button in keymap._buttons_dict.values():
            #     button.configure(border_width=1, border_color="#d4d4d4", font=("맑은 고딕", 15), width=40)
            self.elements.append(keylabel)

clickedButton = ""

class KeyButton(ctk.CTkButton):
    def __init__(self, master, bindFile: str, key: str):
        self.bindFile = bindFile
        super().__init__(
            master=master, 
            text=key, 
            font=("맑은 고딕", 18),
            border_width=1,
            border_color="#d4d4d4",
            fg_color="#292929",
            width=35
        )
        
        self.id = uuid.uuid4()

    def _clicked(self, event=None):
        global clickedButton
        super()._clicked(event)
        if clickedButton != self.id:
            self.configure(fg_color="#206AA4")
            clickedButton = self.id
            index = 0
            for buttons in buttonList:
                idList = list(map(lambda x: x.id, buttons))
                if self.id in idList:
                    index = idList.index(self.id)
                    break
            Keyboard.listenKeyboard(self.bindFile, index)
        else:
            clickedButton = ""
        self.reloadColor()

    def reloadColor(self):
        global buttonList
        for button in sum(buttonList, []):
            if button.id != clickedButton:
                button.configure(fg_color="#292929")



        # original_size = len(self.elements)
        # if original_size < len(eegData):
        #     for index, file in enumerate(eegData[original_size:]):
        #         keylabel = ctk.CTkButton(master=self, text=file, font=("맑은 고딕", 16), width=120, fg_color="#292929", corner_radius=7, hover=False, border_width=1, border_color="#d4d4d4", anchor="w")
        #         keylabel.grid(row=index+original_size, column=0, pady=5, padx=(7, 3), sticky="w")
            
        #         keymap = ctk.CTkSegmentedButton(master=self, values=[], fg_color="#212121", selected_color="#206AA4", unselected_color="#1D1E1E", text_color="#ffffff")
        #         keymap.grid(row=index+original_size, column=1, pady=5)
        #         for button in keymap._buttons_dict.values():
        #             button.configure(border_width=1, border_color="#d4d4d4")
        #         self.elements.append((file, keylabel, keymap))
        # else:
        #     for (file, keylabel, keymap) in [x for x in self.elements if x[0] not in eegData]:
        #         self.elements.remove((file, keylabel, keymap))
        #         keylabel.destroy()
        #         keymap.destroy()
        #         del keybindMap[file]
        #     for index, (_, keylabel, keymap) in enumerate(self.elements):
        #         keylabel.grid_configure(row=index)
        #         keymap.grid_configure(row=index)        