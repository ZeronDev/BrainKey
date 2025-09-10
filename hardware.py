from roboid import HamsterS

class Hardware:
    def __init__(self):
        self.hamster = HamsterS()
    def forward(self):
        hardware.wheels(30)
    def backward(self):
        hardware.wheels(-30)
    def leftward(self):
        hardware.wheels(-30, 30)
    def rightward(self):
        hardware.wheels(30, -30)

#TODO: 테스트, AiProcess에서 Chans 수정
