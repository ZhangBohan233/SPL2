import bin.spl_lib as lib
import bin.configs as cfg

CONFIG_NAME = "mem_configs.cfg"
DEFAULT_CAPACITY = 1048576
DEFAULT_GC_THRESHOLD = 262144


def read_gc_config() -> dict:
    import os
    if os.path.exists(CONFIG_NAME):
        d = cfg.read_cfg(CONFIG_NAME)
        if "memory_size" not in d:
            d["memory_size"] = DEFAULT_CAPACITY
        if "gc_threshold" not in d:
            d["gc_threshold"] = DEFAULT_GC_THRESHOLD
        cfg.write_cfg(CONFIG_NAME, d)
        return d
    else:
        d = {"memory_size": DEFAULT_CAPACITY, "gc_threshold": DEFAULT_GC_THRESHOLD}
        cfg.write_cfg(CONFIG_NAME, d)
        return read_gc_config()


class Pointer:
    def __init__(self, ptr: int):
        self.ptr = ptr


class EnvironmentCarrier:
    def __init__(self):
        pass

    def get_envs(self) -> list:
        raise NotImplementedError


class NativeCollection:
    def __init__(self):
        pass

    def get_pointers(self):
        raise NotImplementedError


class Memory:
    """
    ID reserved:
    0: NULLPTR
    """

    def __init__(self):
        configs = read_gc_config()
        self.capacity = int(configs["memory_size"])
        self.gc_threshold = int(configs["gc_threshold"])

        self.memory = [None for _ in range(self.capacity)]
        self.available = [i for i in range(self.capacity - 1, 0, -1)]

        self.gc_request = False

    def allocate(self, obj) -> int:
        """
        Stores the object to memory and returns the pointer.
        """
        if len(self.available) <= 0:
            raise lib.MemoryException("Memory Overflow")
        loc = self.available.pop()
        self.memory[loc] = obj
        return loc

    def point(self, obj, env) -> Pointer:
        """
        Returns the pointer points to the <SPLObject> object.

        :param obj:
        :param env:
        :return: he pointer points to the <SPLObject> object
        """
        # self.gc_gap += 1
        self.check_gc(env)
        return Pointer(obj.id)

    def ref(self, pointer: Pointer):
        return self.memory[pointer.ptr]

    def free(self, obj):
        self.available.append(obj.id)

    def check_gc(self, env):
        if self.space_available() < self.gc_threshold:
            # self.gc(env)
            self.gc_request = True
            # self.gc_by_env(env)
            # self.gc_gap = 0

    def request_gc(self):
        self.gc_request = True

    def gc(self, env):
        self.gc_request = False
        # s = self.space_available()
        pointed = {0}
        excluded = set()
        self.mark_pointed(env, pointed, excluded)  # Check from innermost
        self.available = []
        for i in range(self.capacity - 1, 0, -1):
            if i not in pointed:
                self.available.append(i)
                # self.memory[i] = None

        # t = self.space_available()
        # print("gc! from {} to {}".format(s, t))

    def space_used(self):
        return self.capacity - len(self.available)

    def space_available(self):
        return len(self.available)

    def mark_pointed(self, env, pointed: set, scanned: set):
        if env is not None and env not in scanned:
            # print(type(env))
            scanned.add(env)
            self.mark_pointed(env.outer, pointed, scanned)
            attrs_ptr = env.attributes_ptr()
            for name in attrs_ptr:
                ptr = attrs_ptr[name]
                if isinstance(ptr, Pointer):
                    pointed.add(ptr.ptr)
                    obj = self.memory[ptr.ptr]
                    # obj = env.get(name, (0, "GC"))
                    if isinstance(obj, EnvironmentCarrier):
                        # print(obj)
                        for stored in obj.get_envs():
                            self.mark_pointed(stored, pointed, scanned)

    def __str__(self):
        return str(self.memory)


MEMORY = Memory()
