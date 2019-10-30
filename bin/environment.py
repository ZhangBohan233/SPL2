from bin import spl_lib as lib

GLOBAL_SCOPE = 0
CLASS_SCOPE = 1
FUNCTION_SCOPE = 2
LOOP_SCOPE = 3
SUB_SCOPE = 4
MODULE_SCOPE = 5


class NullPointer:
    def __init__(self):
        pass

    def __str__(self):
        return "NullPointer"


class Undefined:
    def __init__(self):
        pass

    def __str__(self):
        return "undefined"

    def __repr__(self):
        return self.__str__()


class Annotation(lib.NativeType):
    def __init__(self, name: lib.CharArray, content: lib.Pair = None):
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


NULLPTR = NullPointer()
UNDEFINED = Undefined()

SUPPRESS = Annotation(lib.CharArray("Suppress"))
OVERRIDE = Annotation(lib.CharArray("Override"))


class Environment:
    variables: dict
    constants: dict
    scope_type: int

    """
    ===== Attributes =====
    :param scope_type: the type of scope, whether it is global, class, function or inner
    :param heap: the shared-heap space, all pointed to one
    """

    def __init__(self, scope_type, outer):
        self.scope_type = scope_type
        self.variables: dict = {}  # Stack variables
        self.constants: dict = {}  # Constants

        self.outer: Environment = outer

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
        raise NotImplementedError

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

    def search_namespace(self, key: str):
        raise NotImplementedError

    def assign_namespace(self, key: str, value):
        raise NotImplementedError

    def get_global_const(self, key):
        if self.is_global():
            return self.constants[key]
        else:
            return self.outer.get_global_const(key)

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

    def define_function(self, key, value, lf, annotations: lib.Set):
        if not annotations.contains(OVERRIDE) and \
                not annotations.contains(SUPPRESS) and \
                key[0].islower() and self._local_contains(key):
            lib.compile_time_warning("Warning: re-declaring method '{}' in '{}', at line {}".format(key, lf[1], lf[0]))
        self.variables[key] = value

    def define_var(self, key, value, lf):
        if self._local_contains(key):
            raise lib.NameException("Name '{}' is already defined in this scope, in '{}', at line {}"
                                    .format(key, lf[1], lf[0]))
        else:
            self.variables[key] = value

    def define_const(self, key, value, lf):
        if self.contains_key(key):
            raise lib.NameException("Name '{}' is already defined in this scope, in {}, at line {}"
                                    .format(key, lf[1], lf[0]))
        else:
            self.constants[key] = value

    def assign(self, key, value, lf):
        if key in self.variables:
            self.variables[key] = value
        else:
            out = self.outer
            while out:
                if key in out.variables:
                    out.variables[key] = value
                    return
                out = out.outer
            if not self.assign_const(key, value, lf) and not self.assign_namespace(key, value):
                raise lib.NameException("Name '{}' is not defined, in '{}', at line {}"
                                        .format(key, lf[1], lf[0]))

    def assign_const(self, key, value, lf) -> bool:
        if key in self.constants:
            if self.constants[key] is UNDEFINED:
                self.constants[key] = value
                return True
            else:
                raise lib.NameException("Assignment to constant '{}' is not allowed, in '{}', at line {}"
                                        .format(key, lf[1], lf[0]))
        else:
            out = self.outer
            while out:
                if key in out.constants:
                    if out.constants[key] is UNDEFINED:
                        out.constants[key] = value
                        return True
                    else:
                        raise lib.NameException("Assignment to constant '{}' is not allowed, in '{}', at line {}"
                                                .format(key, lf[1], lf[0]))
                out = out.outer
        return False

    def _local_inner_get(self, key: str):
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
        v = self._local_inner_get(key)
        return v is not NULLPTR

    def _inner_get(self, key: str):
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

        v = self.search_namespace(key)
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
        v = self._inner_get(key)
        # print(key + str(v))
        if v is NULLPTR:
            raise lib.NameException("Name '{}' is not defined, in file '{}', at line {}"
                                    .format(key, line_file[1], line_file[0]))
        return v

    def get_class(self, class_name):
        v = self._inner_get(class_name)
        if v is NULLPTR:
            raise lib.NameException("Class or module '{}' is not defined".format(class_name))
        elif type(v).__name__ == "Function":
            return v.outer_scope.outer.get_class(class_name)
        return v

    def get_global(self):
        if self.is_global():
            return self
        else:
            return self.outer.get_global()

    def contains_key(self, key: str):
        v = self._inner_get(key)
        return v is not NULLPTR

    def attributes(self):
        """
        Returns a union of all local variables in this scope.

        :return: a union of all local variables in this scope
        """
        return {**self.constants, **self.variables}


class MainAbstractEnvironment(Environment):
    namespaces: set

    def __init__(self, scope_type, outer):
        Environment.__init__(self, scope_type, outer)

        self.namespaces = set()

    def is_class(self):
        raise NotImplementedError

    def is_sub(self):
        return False

    def add_namespace(self, namespace: Environment):
        self.namespaces.add(namespace)

    def search_namespace(self, key: str):
        for ns in self.namespaces:
            if key in ns.constants:
                return ns.constants[key]
            if key in ns.variables:
                return ns.variables[key]
        if self.outer:
            return self.outer.search_namespace(key)
        else:
            return NULLPTR

    def assign_namespace(self, key: str, value):
        for ns in self.namespaces:
            if key in ns.variables:
                ns.variables[key] = value
                return True
        if self.outer:
            return self.outer.assign_namespace(key, value)
        else:
            return False


class SubAbstractEnvironment(Environment):
    def __init__(self, scope_type, outer):
        Environment.__init__(self, scope_type, outer)

    def is_sub(self):
        return True

    def is_class(self):
        return False

    def add_namespace(self, namespace):
        raise lib.TypeException("Sub environment does not support namespace definition")

    def search_namespace(self, key: str):
        return self.outer.search_namespace(key)

    def assign_namespace(self, key: str, value):
        return self.outer.assign_namespace(key, value)


class GlobalEnvironment(MainAbstractEnvironment):
    def __init__(self):
        MainAbstractEnvironment.__init__(self, GLOBAL_SCOPE, None)

        # self.modules = {}  # module path : Module objects

    def is_class(self):
        return False

    def is_global(self):
        return True

    # def find_module(self, file_path):
    #     """
    #     Returns a reference to the module.
    #
    #     If the module is already imported, returns the reference to the previous imported one.
    #     Otherwise, adds the module and returns the reference to the the newly added module.
    #
    #     :param file_path:
    #     :return: a reference to the module
    #     """
    #     if file_path in self.modules:
    #         return self.modules[file_path]
    #     else:
    #         return None
    #
    # def add_module(self, file_path, module):
    #     self.modules[file_path] = module


class ModuleEnvironment(MainAbstractEnvironment):
    def __init__(self, outer):
        MainAbstractEnvironment.__init__(self, MODULE_SCOPE, outer)

    def is_class(self):
        return False


class ClassEnvironment(MainAbstractEnvironment):
    def __init__(self, outer):
        MainAbstractEnvironment.__init__(self, CLASS_SCOPE, outer)

    def is_class(self):
        return True


class FunctionEnvironment(MainAbstractEnvironment):
    def __init__(self, outer):
        MainAbstractEnvironment.__init__(self, FUNCTION_SCOPE, outer)

        self.terminated = False
        self.exit_value = None

    def is_class(self):
        return False

    def terminate(self, exit_value):
        self.terminated = True
        self.exit_value = exit_value

    def terminate_value(self):
        return self.exit_value

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
