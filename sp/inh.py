class A:
    def __init__(self):
        self._a = 1
        self.__b = 5

    def __foo(self):
        print(self._a)

    def _bar(self):
        print(self._a + 1)


class B(A):
    def __init__(self):
        A.__init__(self)

    def __foo(self):
        pass

    def _bar(self):
        self.__b = 5


if __name__ == "__main__":
    b = B()
    b._bar()
