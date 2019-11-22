from bin import spl_lib as lib
import bin.spl_memory as mem

GLOBAL_SCOPE = 0
CLASS_SCOPE = 1
FUNCTION_SCOPE = 2
LOOP_SCOPE = 3
SUB_SCOPE = 4
MODULE_SCOPE = 5
NATIVE_OBJECT_SCOPE = 6


class Undefined:
    def __init__(self):
        pass

    def __str__(self):
        return "undefined"

    def __repr__(self):
        return self.__str__()


class Annotation(lib.NativeType):
    def __init__(self, name: lib.CharArray, content=None):
        lib.NativeType.__init__(self)
        self.name = name
        self.params = content

    @classmethod
    def type_name__(cls) -> str:
        return "Annotation"

    def __eq__(self, other):
        return isinstance(other, Annotation) and other.name == self.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        if self.params is None:
            return "@{}".format(self.name)
        else:
            return "@{}({})".format(self.name, self.params)

    def __repr__(self):
        return self.__str__()


NULLPTR = mem.Pointer(0)
UNDEFINED = Undefined()

SUPPRESS = Annotation(lib.CharArray("Suppress"))
OVERRIDE = Annotation(lib.CharArray("Override"))

count = 0


class Environment:
    variables: dict
    constants: dict
    scope_type: int
    env_id: int

    """
    ===== Attributes =====
    :param scope_type: the type of scope, whether it is global, class, function or inner
    :param heap: the shared-heap space, all pointed to one
    """

    def __init__(self, scope_type, outer):
        self.scope_type = scope_type
        self.variables: dict = {}  # Stack variables
        self.constants: dict = {}  # Constants

        global count
        self.env_id = count
        count += 1

        self.outer: Environment = outer
        self.operands = set()

    def __str__(self):
        temp = ["Consts: "]
        for c in self.constants:
            if c != "this":
                temp.append(str(c))
                temp.append(": ")
                temp.append(str(self.constants[c]))
                temp.append(", ")
        temp.append("Vars: ")
        for v in self.variables:
            temp.append(str(v))
            temp.append(": ")
            temp.append(str(self.variables[v]))
            temp.append(", ")
        return "".join(['null' if k is None else k for k in temp])

    def __hash__(self):
        return self.env_id

    def __eq__(self, other):
        return isinstance(other, Environment) and self.env_id == other.env_id

    def add_operand(self, value):
        if isinstance(value, lib.SplObject):
            # print("a", value.id)
            self.operands.add(mem.Pointer(value.id))

    def remove_operand(self, value):
        pass
    #     if isinstance(value, lib.SplObject):
    #         # print("r", value.id)
    #         self.operands.discard(mem.Pointer(value.id))

    def invalidate(self):
        """
        Re-initialize this scope.

        This method will only be called in a scope under level 'LOOP_SCOPE', although this access will not
        be checked.

        :return: None
        """
        self.variables.clear()
        self.constants.clear()

    def is_module(self):
        return self.scope_type == MODULE_SCOPE

    def is_global(self):
        return False

    def is_class(self):
        return False

    def is_sub(self):
        """
        Returns True iff this scope is a NOT a main scope.

        A 'main scope' is a scope that has its independent variable layer. GLOBAL_SCOPE, CLASS_SCOPE and
        FUNCTION_SCOPE are main scopes.

        :return:
        """
        raise NotImplementedError

    def add_namespace(self, namespace):
        raise NotImplementedError

    def search_namespace_ptr(self, key: str):
        raise NotImplementedError

    def assign_namespace_ptr(self, key: str, value):
        raise NotImplementedError

    def get_global_const(self, key):
        ptr = self.get_global_const_ptr(key)
        if isinstance(ptr, mem.Pointer):
            return mem.MEMORY.ref(ptr)
        else:
            return ptr

    def get_global_const_ptr(self, key):
        if self.is_global():
            if key in self.constants:
                return self.constants[key]
            else:
                raise lib.NameException("Global name '{}' is not defined"
                                        .format(key))
        else:
            return self.outer.get_global_const_ptr(key)

    def terminate(self, exit_value):
        raise lib.SplException("Return outside function.")

    def is_terminated(self):
        """
        Returns True iff this scope or one of its parent scopes had been terminated.

        :return: True iff this scope or one of its parent scopes had been terminated
        """
        return False

    def terminate_value(self):
        """
        Returns the last recorded terminate value of a function scope that the function had returned early.

        :return: the terminate value
        """
        raise lib.SplException("Terminate value outside function.")

    def is_broken_or_paused(self):
        return False

    def break_loop(self):
        raise lib.SplException("Break not inside loop.")

    def pause_loop(self):
        """
        Pauses the loop for one iteration.

        This method is called when the keyword 'continue' is executed.

        :return: None
        """
        raise lib.SplException("Continue not inside loop.")

    def resume_loop(self):
        """
        Resumes a paused loop environment.

        If this scope is not paused, this method can still be called but makes no effect.

        :return: None
        """
        raise lib.SplException("Not inside loop.")

    def define_function(self, key, value, lf, annotations):
        if not annotations.contains(OVERRIDE) and \
                not annotations.contains(SUPPRESS) and \
                key[0].islower() and self._local_contains(key):
            lib.compile_time_warning("Warning: re-declaring method '{}' in '{}', at line {}".format(key, lf[1], lf[0]))
        # self.variables[key] = value
        self.variables[key] = mem.MEMORY.point(value, self)  # must be reference type

    def define_var(self, key, value, lf):
        if self._local_contains(key):
            raise lib.NameException("Name '{}' is already defined in this scope, in '{}', at line {}"
                                    .format(key, lf[1], lf[0]))
        else:
            if isinstance(value, lib.SplObject):
                self.variables[key] = mem.MEMORY.point(value, self)  # reference type
            else:
                self.variables[key] = value  # primitive type

    def define_const(self, key, value, lf):
        if self.contains_key(key):
            raise lib.NameException("Name '{}' is already defined in this scope, in {}, at line {}"
                                    .format(key, lf[1], lf[0]))
        else:
            if isinstance(value, lib.SplObject):
                self.constants[key] = mem.MEMORY.point(value, self)  # reference type
            else:
                self.constants[key] = value  # primitive type

    def assign(self, key, value, lf):
        if isinstance(value, lib.SplObject):
            ptr = mem.MEMORY.point(value, self)
            self.assign_ptr(key, ptr, lf)
        else:
            self.assign_ptr(key, value, lf)

    def assign_ptr(self, key, ptr, lf):
        if key in self.variables:
            self.variables[key] = ptr
            # self.variables[key] = value
        else:
            out = self.outer
            while out:
                if key in out.variables:
                    out.variables[key] = ptr
                    # out.variables[key] = value
                    return
                out = out.outer
            if not self.assign_const_ptr(key, ptr, lf) and not self.assign_namespace_ptr(key, ptr):
                raise lib.NameException("Name '{}' is not defined, in '{}', at line {}"
                                        .format(key, lf[1], lf[0]))

    def assign_const_ptr(self, key, ptr, lf) -> bool:
        if key in self.constants:
            cur_ptr = self.constants[key]
            if mem.MEMORY.ref(cur_ptr) is UNDEFINED:
                # self.constants[key] = value
                self.constants[key] = ptr
                return True
            else:
                raise lib.NameException("Assignment to constant '{}' is not allowed, in '{}', at line {}"
                                        .format(key, lf[1], lf[0]))
        else:
            out = self.outer
            while out:
                if key in out.constants:
                    cur_ptr = self.constants[key]
                    if mem.MEMORY.ref(cur_ptr) is UNDEFINED:
                        # out.constants[key] = value
                        out.constants[key] = ptr
                        return True
                    else:
                        raise lib.NameException("Assignment to constant '{}' is not allowed, in '{}', at line {}"
                                                .format(key, lf[1], lf[0]))
                out = out.outer
        return False

    def _local_inner_get_ptr(self, key: str):
        if key in self.constants:
            return self.constants[key]
        if key in self.variables:
            return self.variables[key]

        out = self
        while out.outer and out.is_sub():
            out = out.outer

            if key in out.constants:
                return out.constants[key]
            if key in out.variables:
                return out.variables[key]

        return NULLPTR

    def _local_contains(self, key: str) -> bool:
        """
        Returns True iff this main scope has this key, or the heap has this key.

        :param key:
        :return:
        """
        v = self._local_inner_get_ptr(key)
        return v is not NULLPTR

    def _inner_get_ptr(self, key: str):
        """
        Internally gets a value stored in this scope, 'NULLPTR' if not found.

        :param key:
        :return:
        """
        if key in self.constants:
            return self.constants[key]
        if key in self.variables:
            return self.variables[key]

        out = self.outer
        while out:
            if key in out.constants:
                return out.constants[key]
            if key in out.variables:
                return out.variables[key]

            out = out.outer

        v = self.search_namespace_ptr(key)
        if v is not NULLPTR:
            return v

        return NULLPTR

    def get(self, key: str, line_file: tuple):
        """
        Returns the value of that key.

        If the value is a pointer, then returns the instance pointed by the pointer instead.

        :param key:
        :param line_file:
        :return: the value corresponding to the key. Instance will be returned if the value is a pointer.
        """
        ptr = self.get_ptr(key, line_file)
        if isinstance(ptr, mem.Pointer):
            return mem.MEMORY.ref(ptr)
        else:
            return ptr

    def get_ptr(self, key: str, line_file: tuple):
        v = self._inner_get_ptr(key)
        # print(key + str(v))
        if v is NULLPTR:
            raise lib.NameException("Name '{}' is not defined, in file '{}', at line {}"
                                    .format(key, line_file[1], line_file[0]))
        return v

    def get_class(self, class_name):
        ptr = self.get_class_ptr(class_name)
        return mem.MEMORY.ref(ptr)

    def get_class_ptr(self, class_name):
        v = self._inner_get_ptr(class_name)
        if v is NULLPTR:
            raise lib.NameException("Class or module '{}' is not defined".format(class_name))
        elif type(v).__name__ == "Function":
            return v.outer_scope.outer.get_class_ptr(class_name)
        return v

    def get_global(self):
        if self.is_global():
            return self
        else:
            return self.outer.get_global()

    def contains_key(self, key: str):
        v = self._inner_get_ptr(key)
        return v is not NULLPTR

    def attributes_ptr(self):
        """
        Returns a union of all local variables in this scope.

        :return: a union of all local variables in this scope
        """
        return {**self.constants, **self.variables}

    def attributes(self):
        # print(self.attributes_ptr())
        d = self.attributes_ptr()
        pd = {}
        for k in d:
            p = d[k]
            if isinstance(p, mem.Pointer):
                pd[k] = mem.MEMORY.ref(p)
            else:
                pd[k] = p
        return pd


class MainAbstractEnvironment(Environment):
    namespaces: set

    def __init__(self, scope_type, outer):
        Environment.__init__(self, scope_type, outer)

        self.namespaces = set()

    def is_sub(self):
        return False

    def add_namespace(self, namespace: Environment):
        self.namespaces.add(namespace)

    def search_namespace_ptr(self, key: str) -> mem.Pointer:
        for ns in self.namespaces:
            if key in ns.constants:
                return ns.constants[key]
            if key in ns.variables:
                return ns.variables[key]
        if self.outer:
            return self.outer.search_namespace_ptr(key)
        else:
            return NULLPTR

    def assign_namespace_ptr(self, key: str, ptr):
        for ns in self.namespaces:
            if key in ns.variables:
                ns.variables[key] = ptr
                # ns.variables[key] = value
                return True
        if self.outer:
            return self.outer.assign_namespace_ptr(key, ptr)
        else:
            return False


class SubAbstractEnvironment(Environment):
    def __init__(self, scope_type, outer):
        Environment.__init__(self, scope_type, outer)

    def is_sub(self):
        return True

    def add_namespace(self, namespace):
        raise lib.TypeException("Sub environment does not support namespace definition")

    def search_namespace_ptr(self, key: str):
        return self.outer.search_namespace_ptr(key)

    def assign_namespace_ptr(self, key: str, value):
        return self.outer.assign_namespace_ptr(key, value)


class GlobalEnvironment(MainAbstractEnvironment):
    def __init__(self):
        MainAbstractEnvironment.__init__(self, GLOBAL_SCOPE, None)

        # self.expr_count = 0

    # def gc_able(self):
    #     return self.expr_count == 0

    def is_global(self):
        return True


class ModuleEnvironment(MainAbstractEnvironment):
    def __init__(self, outer):
        MainAbstractEnvironment.__init__(self, MODULE_SCOPE, outer)

    def is_class(self):
        return False


class ClassEnvironment(MainAbstractEnvironment):
    instance = None  # reference to the instance

    def __init__(self, outer):
        MainAbstractEnvironment.__init__(self, CLASS_SCOPE, outer)

    def is_class(self):
        return True


class NativeObjectEnvironment(MainAbstractEnvironment):

    def __init__(self):
        MainAbstractEnvironment.__init__(self, NATIVE_OBJECT_SCOPE, None)

    def delete_var(self, key, lf):
        if not self.contains_key(key):
            lib.NameException("Name '{}' is not defined in this scope, in {}, at line {}"
                              .format(key, lf[1], lf[0]))
        self.variables.pop(key)


class FunctionEnvironment(MainAbstractEnvironment):
    def __init__(self, outer):
        MainAbstractEnvironment.__init__(self, FUNCTION_SCOPE, outer)

        self.terminated = False
        self.exit_value = None

    def terminate(self, exit_value):
        self.terminated = True
        # self.exit_value = exit_value
        self.define_var("return value", exit_value, (0, "Environment"))

    def terminate_value(self):
        return self.get("return value", (0, "Environment"))
        # return self.exit_value

    def is_terminated(self):
        return self.terminated


class LoopEnvironment(SubAbstractEnvironment):
    def __init__(self, outer):
        SubAbstractEnvironment.__init__(self, LOOP_SCOPE, outer)

        self.broken = False
        self.paused = False

    def resume_loop(self):
        self.paused = False

    def terminate(self, exit_value):
        self.broken = True
        self.outer.terminate(exit_value)

    def terminate_value(self):
        return self.outer.terminate_value()

    def is_terminated(self):
        return self.outer.is_terminated()

    def is_broken_or_paused(self):
        return self.broken or self.paused

    def break_loop(self):
        self.broken = True

    def pause_loop(self):
        self.paused = True


class SubEnvironment(SubAbstractEnvironment):
    def __init__(self, outer):
        SubAbstractEnvironment.__init__(self, SUB_SCOPE, outer)

    def resume_loop(self):
        self.outer.resume_loop()

    def terminate(self, exit_value):
        self.outer.terminate(exit_value)

    def terminate_value(self):
        return self.outer.terminate_value()

    def is_terminated(self):
        return self.outer.is_terminated()

    def is_broken_or_paused(self):
        return self.outer.is_broken_or_paused()

    def break_loop(self):
        self.outer.break_loop()

    def pause_loop(self):
        self.outer.pause_loop()
