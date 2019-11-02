import bin.spl_lib as lib
import bin.configs as cfg

CONFIG_NAME = "mem_configs.cfg"
DEFAULT_CAPACITY = 1048576
DEFAULT_GC_THRESHOLD = 262144
DEFAULT_GC_GAP = 16384


def read_gc_config() -> dict:
    import os
    if os.path.exists(CONFIG_NAME):
        d = cfg.read_cfg(CONFIG_NAME)
        if "memory_size" not in d:
            d["memory_size"] = DEFAULT_CAPACITY
        if "gc_threshold" not in d:
            d["gc_threshold"] = DEFAULT_GC_THRESHOLD
        if "gc_gap" not in d:
            d["gc_gap"] = DEFAULT_GC_GAP
        cfg.write_cfg(CONFIG_NAME, d)
        return d
    else:
        d = {"memory_size": DEFAULT_CAPACITY, "gc_threshold": DEFAULT_GC_THRESHOLD, "gc_gap": DEFAULT_GC_GAP}
        cfg.write_cfg(CONFIG_NAME, d)
        return read_gc_config()


class Memory:
    """
    ID reserved:
    0: NULLPTR
    """

    def __init__(self):
        configs = read_gc_config()
        self.capacity = int(configs["memory_size"])
        self.gc_threshold = int(configs["gc_threshold"])
        self.least_gc_gap = int(configs["gc_gap"])

        self.gc_gap = 0
        self.memory = [None for _ in range(self.capacity)]
        self.available = [i for i in range(self.capacity - 1, 0, -1)]

    def allocate(self, obj, env) -> int:
        """
        Stores the object to memory and returns the pointer.
        """
        self.gc_gap += 1
        self.check_gc(env)
        loc = self.available.pop()
        self.memory[loc] = obj
        if isinstance(obj, lib.SplObject):
            obj.id = loc
        return loc

    def ref(self, pointer: int):
        return self.memory[pointer]

    def free(self, p: int):
        self.available.append(p)

    def check_gc(self, env):
        if self.space_available() <= 0:
            self.gc(env)
            self.gc_gap = 0
            if self.space_available():
                raise lib.MemoryException("Memory Overflow")
        if self.gc_gap >= self.least_gc_gap and self.space_available() < self.gc_threshold:
            # s = self.space_available()
            self.gc(env)
            self.gc_gap = 0
            # t = self.space_available()
            # print("gc! from {} to {}".format(s, t))

    def gc(self, env):
        global_env = env.get_global()
        pointed = {0}
        mark_pointed(global_env, pointed)
        self.available = []
        for i in range(self.capacity - 1, 0, -1):
            if i not in pointed:
                self.available.append(i)

    def space_used(self):
        return self.capacity - len(self.available)

    def space_available(self):
        return len(self.available)

    def __str__(self):
        return str(self.memory)


def mark_pointed(env, lst: set):
    attrs_ptr = env.attributes_ptr()
    for name in attrs_ptr:
        lst.add(attrs_ptr[name])
    for sub_env in env.children:
        mark_pointed(sub_env, lst)


MEMORY = Memory()
