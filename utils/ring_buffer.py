
class RingBuffer(object):
    def __init__(self, size):
        self.capacity = size
        self.clear()

    def append(self, x):
        self.data.pop(0)
        self.data.append(x)
        if self.size < self.capacity:
            self.size += 1

    def update(self, pos, x):
        if -self.capacity <= pos < self.capacity:
            self.data[pos] = x

    def clear(self):
        self.size = 0
        self.data = [None for i in range(self.capacity)]

    def isfull(self):
        return self.size == self.capacity

    def assignment(self, x):
        if len(x) >= self.capacity:
            self.data = x[-self.capacity:]
        else:
            self.clear()
            self.data[-len(x):] = x[-len(x):]

        if self.size < self.capacity:
            self.size += len(x)
        self.size = min(self.size, self.capacity)

    def get(self):
        return self.data
