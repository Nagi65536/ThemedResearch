from time import sleep


class Subject:
    def __init__(self):
        self._button_state = 0

    @property
    def button_state(self):
        return self._button_state

    @button_state.setter
    def button_state(self, state):
        if self._button_state != state:
            self._button_state = state
            print("buttonの状態が変化")


class Observer:
    def reaction(self):
        pass


def observer():
    A = Observer()
    Button = Subject()
    sleep(10)
    Button.button_state = 1  # =>buttonの状態が変化


import random
if __name__ == "__main__":
    a = [1,2,3]
    b = random.choice(a)
    print(b)
    print(a.remove(b))
    print(a)