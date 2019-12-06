import bin.spl_lib as lib
import bin.configs as cfg

CONFIG_NAME = "mem_configs.cfg"
DEFAULT_CAPACITY = 1048576
DEFAULT_STACK = 1024


def read_gc_config() -> dict:
    import os
    if os.path.exists(CONFIG_NAME):
        d = cfg.read_cfg(CONFIG_NAME)
        if "heap_size" not in d:
            d["heap_size"] = DEFAULT_CAPACITY
        if "stack_size" not in d:
            d["stack_size"] = DEFAULT_STACK
        cfg.write_cfg(CONFIG_NAME, d)
        return d
    else:
        d = {"heap_size": DEFAULT_CAPACITY, "stack_size": DEFAULT_STACK}
        cfg.write_cfg(CONFIG_NAME, d)
        return read_gc_config()


class Pointer:
    def __init__(self, ptr: int):
        self.ptr = ptr

    def __hash__(self):
        return hash(self.ptr)

    def __eq__(self, other):
        return isinstance(other, Pointer) and other.ptr == self.ptr

    def __str__(self):
        return "<Pointer to {}>".format(self.ptr)

    def __repr__(self):
        return self.__str__()


class EnvironmentCarrier:
    def __init__(self):
        pass

    def get_envs(self) -> list:
        raise NotImplementedError

    def malloc_inner(self, self_loc: int):
        pass


class Memory:
    """
    ID reserved:
    0: NULLPTR
    """

    def __init__(self):
        configs = read_gc_config()
        self.stack_size = int(configs["stack_size"])
        self.heap_size = int(configs["heap_size"])

        self.sp = 1
        self.call_stack = []

        self.memory = [None for _ in range(self.heap_size + self.stack_size)]  # front: stack, back: heap
        self.available = [i + self.stack_size for i in range(self.heap_size - 1, -1, -1)]

    def call(self):
        self.call_stack.append(self.sp)

    def exit_call(self):
        self.sp = self.call_stack.pop()

    def allocate(self, obj, length=1) -> int:
        """
        Stores the object to memory and returns the pointer.
        """
        if self.sp >= self.stack_size:
            raise lib.MemoryException("Stack Overflow")
        if len(self.call_stack) == 0:
            return self._heap_alloc(obj, length)
        else:
            loc = self.sp
            self.memory[loc] = obj
            self.sp += length
            return loc

    def point(self, obj, lf) -> Pointer:
        """
        Returns the pointer points to the <SPLObject> object.

        :param obj:
        :param lf
        :return: the pointer points to the <SPLObject> object
        """
        ptr = Pointer(obj.id)
        self._check_in_stack(ptr, lf)
        return ptr

    def set_ret(self, ptr_pri) -> Pointer:
        sp = self.sp
        self.sp += 1
        self.memory[sp] = ptr_pri
        return Pointer(sp)

    def ref(self, pointer: Pointer, lf):
        self._check_in_stack(pointer, lf)
        return self.memory[pointer.ptr]

    def access(self, loc):
        return self.memory[loc]

    def set(self, loc, value):
        self.memory[loc] = value

    def malloc(self, obj, length=1) -> int:
        return self._heap_alloc(obj, length, True)

    def free(self, obj):
        length = obj.memory_length()
        for i in range(length):
            loc = obj.id + length - i - 1
            self._check_in_heap(loc, obj)
            self.available.append(loc)
            self.memory[loc] = None  # only for test

    def _check_in_heap(self, i, obj):
        if i < self.stack_size:
            raise lib.MemoryException("Object {} at {} is not in heap".format(i, obj))

    def _heap_alloc(self, obj, length, replace=False):
        if len(self.available) <= 0:
            raise lib.MemoryException("Memory Overflow")
        if hasattr(obj, "id") and obj.id >= self.stack_size:  # already allocated in heap
            return obj.id
        ind = self._find_available(length)
        loc = self.available[ind]
        self.available[ind - length + 1: ind + 1] = []
        if replace:
            self.memory[obj.id] = None
        self.memory[loc] = obj
        obj.id = loc
        return loc

    def _check_in_stack(self, pointer: Pointer, lf):
        if pointer.ptr < self.stack_size and len(self.call_stack) > 0:
            # if pointer.ptr < self.call_stack[-1]:
            #     raise lib.MemoryException("Unreachable stack address {}: calling from stack top to stack body. Top: "
            #                               "{}, sp: {} .In "
            #                               "file '{}', at line {}"
            #                               .format(pointer.ptr, self.call_stack[-1], self.sp, lf[1], lf[0]))
            if pointer.ptr >= self.sp:
                raise lib.MemoryException("Unreachable stack address {}: pointer outside stack, In "
                                          "file '{}', at line {}"
                                          .format(pointer.ptr, lf[1], lf[0]))

    def _find_available(self, length) -> int:
        """
        Finds a consecutive heap address of length <length> and returns the first address.

        :param length:
        :return:
        """
        i = len(self.available) - 1
        while i >= 0:
            j = 0
            while j < length - 1 and i - j > 0:
                if self.available[i - j - 1] != self.available[i - j] + 1:
                    break
                j += 1
            if j == length - 1:
                return i
            else:
                i -= j + 1
        raise lib.MemoryException("No space to malloc an object of length {}".format(length))

    def space_used(self):
        return self.heap_size - len(self.available)

    def space_available(self):
        return len(self.available)

    def __str__(self):
        return str(self.memory[:self.stack_size]) + "\n" + str(self.memory[self.stack_size:])


MEMORY = Memory()
NULL = Pointer(0)
