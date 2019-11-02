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


class EnvironmentCarrier:
    def __init__(self):
        pass

    def get_envs(self) -> list:
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
            self.gc(env)
            self.gc_gap = 0

    def gc(self, env):
        s = self.space_available()
        global_env = env.get_global()
        pointed = {0}
        excluded = set()
        print(type(env).__name__)
        self.mark_pointed(env, pointed, excluded)  # Check from innermost
        self.mark_pointed(global_env, pointed, excluded)  # Check from outermost
        self.available = []
        # print(len(pointed))
        for i in range(self.capacity - 1, 0, -1):
            if i not in pointed:
                self.available.append(i)
        t = self.space_available()
        # print("gc! from {} to {}".format(s, t))
        # print(len(excluded))

    def space_used(self):
        return self.capacity - len(self.available)

    def space_available(self):
        return len(self.available)

    def __str__(self):
        return str(self.memory)

    def mark_pointed(self, env, set_: set, excluded: set):
        if env is not None and env not in excluded:
            excluded.add(env)
            attrs_ptr = env.attributes_ptr()
            for name in attrs_ptr:
                ptr = attrs_ptr[name]
                set_.add(ptr)
                obj = self.memory[ptr]
                self.mark_pointed(env.outer, set_, excluded)
                if isinstance(obj, EnvironmentCarrier):
                    for stored in obj.get_envs():
                        self.mark_pointed(stored, set_, excluded)


MEMORY = Memory()
