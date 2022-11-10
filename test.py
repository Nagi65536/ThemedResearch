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


if __name__ == "__main__":
    print([i for i in range(1,7)])
    # dict_ = [[0, 'a'], [1, 'b'], [2, 'c']]
    # print([{'p':d[0], 'q':d[1]} for d in dict_])
    # a = [1,2,3]
    # b = random.choice(a)
    # print(b)
    # print(a.remove(b))
    # print(a)