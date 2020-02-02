class Filter:
    def __init__(self, size=3, coef=0.9, t=1, dt=0.02):
        self.coef = coef
        self.size = size
        self.T = t
        self.dt = dt
        self.values = self.empty_array()
        self.data = self.empty_array()
        self.prev_data = self.empty_array()

    def empty_array(self):
        values = []
        for index in range(self.size):
            values.append(0)
        return values

    def add(self, data):
        self.data = data
        K = self.dt / self.T / 2.0
        K1 = self.dt / self.T
        for index in range(self.size):
            # self.values[index] = (1 - self.coef) * self.values[index] + self.coef * self.data[index]
            self.values[index] = self.values[index] * (1 - K) / (1 + K) + \
                                 (self.data[index] + self.prev_data[index]) * K / (1 + K)
            # self.values[index] = self.values[index] * (1 - K1) + K1 * self.data[index]
            self.prev_data[index] = self.data[index]

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
