class Filter:
    def __init__(self, size=3, coef=0.9):
        self.coef = coef
        self.size = size
        self.values = self.empty_array()
        self.data = self.empty_array()

    def empty_array(self):
        values = []
        for index in range(self.size):
            values.append(0)
        return values

    def add(self, data):
        self.data = data
        for index in range(self.size):
            self.values[index] = (1 - self.coef) * self.values[index] + self.coef * self.data[index]

    def get(self):
        return self.values


if __name__ == "__main__":
    filter = Filter()
    filter.add([0, 0, 0])
    filter.add([0, 0, 0])
    filter.add([0, 0, 0])
    filter.add([1, 1, 1])
    print(filter.get())
    filter.add([1, 1, 1])
    print(filter.get())
    filter.add([1, 1, 1])
    print(filter.get())
