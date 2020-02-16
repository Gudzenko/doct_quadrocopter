class Filter:
    def __init__(self, size=3, t=1, dt=0.02):
        self.size = size
        self.T = t
        self.dt = dt
        self.values = self.empty_array()
        self.data = self.empty_array()
        self.prev_data = self.empty_array()
        self.prev_data_array = self.empty_n_array(length=6)

    def empty_array(self):
        values = []
        for index in range(self.size):
            values.append(0)
        return values

    def empty_n_array(self, length):
        data = []
        for index1 in range(length):
            values = []
            for index2 in range(self.size):
                values.append(0)
            data.append(values)
        return data

    def add_to_prev_data_array(self, new_values):
        self.prev_data_array.pop()
        self.prev_data_array.insert(0, new_values.copy())

    def add(self, data):
        self.data = data
        K = self.dt / self.T / 2.0
        for index in range(self.size):
            self.values[index] = self.values[index] * (1 - K) / (1 + K) + \
                                 (self.data[index] + self.prev_data[index]) * K / (1 + K)
            self.prev_data[index] = self.data[index]
        self.add_to_prev_data_array(self.values)

    def get(self):
        return self.values

    def prediction(self, t=None):
        if t is None:
            t = self.dt
        # coef = [213.0 / 48.0, -397.0 / 48.0, 402.0 / 48.0, -234.0 / 48.0, 73.0 / 48.0, -9.0 / 48.0]
        coef = [35.0 / 12.0, -39.0 / 12.0, 21.0 / 12.0, -5.0 / 12.0]
        values = self.empty_array()
        for index1 in range(self.size):
            for index2 in range(len(coef)):
                values[index1] += coef[index2] * self.prev_data_array[index2][index1]
        if 0 < t < self.dt:
            for index in range(self.size):
                values[index] = values[index] * t / self.dt + self.prev_data_array[0][index] * (1 - t / self.dt)
        return values


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
