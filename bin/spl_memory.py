class Pointer:
    def __init__(self, pointer):
        self.pointer: int = pointer


# class Memory:
#     def __init__(self):
#         self.counter = 0
#         self.capacity = 1024
#         self.memory = [None for _ in range(self.capacity)]
#         self.available = [self.capacity - i - 1 for i in range(self.capacity)]
#
#     def allocate(self, obj) -> Pointer:
#         """
#         Stores the object to memory and returns the pointer.
#
#         :type obj: SplObject
#         :return:
#         """
#         loc = self.available.pop()
#         self.memory[loc] = obj
#         return Pointer(loc)
#
#     def ref(self, pointer: Pointer):
#         return self.memory[pointer.pointer]
#
#     def free(self, p: Pointer):
#         self.available.append(p.pointer)


class Memory:
    def __init__(self):
        self.object_counter = 0
        self.store = 0

    def allocate(self) -> int:
        """
        returns the current pointer.

        :return:
        """
        p = self.object_counter
        self.object_counter += 1
        return p

    def store_status(self):
        self.store = self.object_counter

    def restore_status(self):
        self.object_counter = self.store


MEMORY = Memory()
