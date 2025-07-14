import customtkinter as ctk
import os
from Util import path
from DataManager import eegData, keybindMap, reload

class KeybindSelector(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master=master,fg_color="transparent")
        self.elements = []
        self.listElement()
    def refresh(self):
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
        
        for element in self.elements:
            element[0].destroy()
            element[1].destroy()
        eegData.clear()
        eegData.extend(reload())
        self.elements.clear()
        self.listElement()
        
    def listElement(self):
        for index, file in enumerate(eegData):
            keylabel = ctk.CTkButton(master=self, text=file, font=("맑은 고딕", 16), width=120, fg_color="#292929", corner_radius=7, hover=False, border_width=1, border_color="#d4d4d4", anchor="w")
            keylabel.grid(row=index, column=0, pady=5, padx=(7, 4), sticky="w")
            
            keymap = ctk.CTkSegmentedButton(master=self, values=keybindMap.get(file, []), fg_color="#212121", selected_color="#206AA4", unselected_color="#1D1E1E", text_color="#ffffff")
            keymap.grid(row=index, column=1, pady=5)
            for button in keymap._buttons_dict.values():
                button.configure(border_width=1, border_color="#d4d4d4")
            self.elements.append((keylabel, keymap))