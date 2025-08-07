import os

stopped = False
other_screen = None
disabled = False
app = None

def path(*args):
    return os.path.join(os.getcwd(), *args)
def toggleAbility():
    global disabled
    disabled = not disabled
