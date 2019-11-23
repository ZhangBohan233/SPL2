class M:
    def __init__(self):
        self.stack_size = 10
        self.heap_size = 10
        self.available = [19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 3, 2, 0]

    def find_available(self, length) -> int:
        """
        Finds a consecutive heap address of length <length> and returns the first address.

        :param length:
        :return:
        """
        # i = len(self.available) - 1
        # while i >= 0:
        #     j = 0
        #     while j < length - 1 and i - j > 0:
        #         if self.available[i - j - 1] != self.available[i - j] + 1:
        #             break
        #         j += 1
        #     if j == length - 1:
        #         return i
        #     else:
        #         i -= j + 1
        # return -1

    def ava(self, length):
        ind = self.find_available(length)
        self.available[ind - length + 1: ind + 1] = []


if __name__ == "__main__":
    m = M()
    print(m.ava(1))
    print(m.available)
