import bin.environment as environment
import bin.spl_lib as lib
import bin.spl_memory as mem


LINE_FILE = 0, "Interpreter"


class Array(lib.NativeType, lib.Iterable, mem.EnvironmentCarrier):
    """
    A collector of sequential data with static size and dynamic type.
    """
    def __init__(self, *initial):
        lib.NativeType.__init__(self)

        self.length = len(initial)
        self.env = environment.NativeObjectEnvironment()
        # self.list = [*initial]
        for i in range(len(initial)):
            self.env.define_var(str(i), initial[i], LINE_FILE)

    def __iter__(self):
        return (self.env.get(str(i), LINE_FILE) for i in range(self.length))

    def __str__(self):
        return str([lib.CharArray(lib.get_string_repr(v)) for v in self])

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self.env.get(str(item), LINE_FILE)
        # return self.list[item]

    def __setitem__(self, key, value):
        self.env.assign(str(key), value, LINE_FILE)
        # self.list[key] = value

    def get_envs(self) -> list:
        # print(self.env)
        return [self.env]

    def as_py_list(self):
        return [self.env.get(str(i), LINE_FILE) for i in range(self.length)]

    def get_pointers(self):
        pass

    @classmethod
    def type_name__(cls):
        return "Array"

    def contains(self, item):
        return item in self.__iter__()
        # return item in self.list

    def size(self):
        return self.length
        # return len(self.list)

    def sub_array(self, from_, to=None):
        length = self.size()
        end = length if to is None else to
        if from_ < 0 or end > length:
            raise lib.IndexOutOfRangeException("Sub array index out of range")
        # return Array(self.list[from_: end])
        return Array([self[i] for i in range(from_, to, 1)])

    # def reverse(self):
    #     return self.list.reverse()


class Pair(lib.NativeType, lib.Iterable, mem.EnvironmentCarrier):
    def __init__(self, initial: dict):
        lib.NativeType.__init__(self)

        # self.pair = initial.copy()
        self.ele_num = len(initial)
        self.env = environment.NativeObjectEnvironment()
        for k in initial:
            self.env.define_var(k, initial[k], LINE_FILE)

    def __iter__(self):
        return (k for k in self.env.attributes_ptr())

    def __str__(self):
        return str({lib.CharArray(lib.get_string_repr(k)):
                        lib.CharArray(lib.get_string_repr(self[k])) for k in self})

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self.env.get(item, LINE_FILE)
        # return self.pair[item]

    def __setitem__(self, key, value):
        if key not in self:
            self.ele_num += 1
            self.env.define_var(key, value, LINE_FILE)
        else:
            self.env.assign(key, value, LINE_FILE)
        # self.pair[key] = value

    def contains(self, item):
        return self.env.contains_key(item)

    def get(self, key):
        return self.__getitem__(key)

    def put(self, key, value):
        self.__setitem__(key, value)

    def size(self):
        return self.ele_num

    @classmethod
    def type_name__(cls):
        return "Pair"

    def get_envs(self) -> list:
        return [self.env]


class Set(lib.NativeType, lib.Iterable, mem.EnvironmentCarrier):
    def __init__(self, *initial):
        lib.NativeType.__init__(self)

        # self.set = set(initial)
        self.ele_num = len(initial)
        self.env = environment.NativeObjectEnvironment()
        for e in initial:
            self.env.define_var(str(hash(e)), e, LINE_FILE)

    def __iter__(self):
        return (self.env.get(v, LINE_FILE) for v in self.env.attributes_ptr())

    def __str__(self):
        return str(set([lib.CharArray(lib.get_string_repr(v)) for v in self]))

    def __repr__(self):
        return self.__str__()

    def __contains__(self, item):
        return self.env.contains_key(str(hash(item)))

    def get(self, item):
        if item in self:
            h = str(hash(item))
            return self.env.get(h, LINE_FILE)

    def size(self):
        return self.ele_num

    def add(self, item):
        if item not in self:
            self.ele_num += 1
            self.env.define_var(str(hash(item)), item, LINE_FILE)
        else:
            self.env.assign(str(hash(item)), item, LINE_FILE)

    # def pop(self):
    #     self.env.

    def clear(self):
        self.env.invalidate()

    def union(self, other):
        for e in other:
            self.add(e)
        # self.set.union(other)

    # def update(self, s):
    #     self.set.update(s)

    def contains(self, item):
        return item in self

    @classmethod
    def type_name__(cls):
        return "Set"

    def get_envs(self) -> list:
        return [self.env]


class File(lib.NativeType):
    """
    An opened file object.
    """

    def __init__(self, fp, mode):
        lib.NativeType.__init__(self)

        self.mode: str = mode
        self.fp = fp

    def read_one(self):
        """
        Reads one unit from the file.

        :return: the next unit in tis file
        """
        r = self.fp.read(1)
        if r:
            if self.mode == "r":
                return lib.CharArray(r)
            elif self.mode == "rb":
                return int(self.fp.read(1)[0])
            else:
                raise lib.PyIOException("Wrong mode")
        else:
            return None

    def read(self):
        """
        Reads all contents of this file.

        :return: all contents of this file
        """
        if self.mode == "r":
            return lib.CharArray(self.fp.read())
        elif self.mode == "rb":
            return Array(*list(self.fp.read()))
        else:
            raise lib.PyIOException("Wrong mode")

    def readline(self):
        """
        Reads the next line from this file.

        This method only works for text file.

        :return: the next line from this file
        """
        if self.mode == "r":
            s = self.fp.readline()
            if s:
                return lib.CharArray(s)
            else:
                return None
        else:
            raise lib.PyIOException("Wrong mode")

    def write(self, s):
        """
        Writes the content to this file

        :param s: the content to be written
        """
        if "w" in self.mode:
            if "b" in self.mode:
                self.fp.write(bytes(s))
            else:
                self.fp.write(str(s))
        else:
            raise lib.PyIOException("Wrong mode")

    def flush(self):
        """
        Flushes all buffered contents to the file.
        """
        if "w" in self.mode:
            self.fp.flush()
        else:
            raise lib.PyIOException("Wrong mode")

    def close(self):
        """
        Closes this file.
        """
        self.fp.close()

    @classmethod
    def type_name__(cls):
        return "File"

