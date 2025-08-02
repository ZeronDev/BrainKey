import os

def path(*args):
    return os.path.join(os.getcwd(), *args)
def toggleAbility():
    disabled = not disabled
stopped = False
other_screen = None
disabled = False
app = None