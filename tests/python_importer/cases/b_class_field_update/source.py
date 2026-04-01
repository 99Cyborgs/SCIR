class Counter:
    def __init__(self, value):
        self.value = value

    def bump(self, step):
        self.value = step(self.value)
        return self.value
