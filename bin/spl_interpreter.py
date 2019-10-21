from bin import spl_lexer as lex, spl_ast as ast, spl_token_lib as stl, spl_parser as psr, spl_memory as mem
import bin.spl_lib as lib
import bin.graphic_lib as gra
import script
import multiprocessing
import math
import inspect
import os
import subprocess
import traceback
from bin.environment import Environment, GlobalEnvironment, LoopEnvironment, SubEnvironment, \
    FunctionEnvironment, ClassEnvironment, ModuleEnvironment, UNDEFINED, Annotation

LST = [72, 97, 112, 112, 121, 32, 66, 105, 114, 116, 104, 100, 97, 121, 32,
       73, 115, 97, 98, 101, 108, 108, 97, 33, 33, 33]

LINE_FILE = 0, "interpreter"
INVALID = lib.InvalidArgument()
UNPACK_ARGUMENT = lib.UnpackArgument()
KW_UNPACK_ARGUMENT = lib.KwUnpackArgument()

PRIMITIVE_TYPE_TABLE = {
    "boolean": "bool",
    "void": "NoneType"
}


class Interpreter:
    """
    A spl interpreter entry object.

    This class is used to create an spl evaluator, which is mostly used to interpret the root 'BlockStmt' of
    a program.
    """

    def __init__(self, argv: list, directory: str, encoding: str, in_out_err: tuple):
        # mem.start()
        self.ast = None
        self.argv = argv
        self.dir = directory
        self.encoding = encoding
        self.in_out_err = in_out_err
        self.env = GlobalEnvironment()
        self.env.scope_name = "Global"
        self.set_up_env()
        self.handler = self.default_handler

    def set_up_env(self):
        """
        Sets up the global environment.

        :return:
        """
        add_natives(self.env)
        # obj = lib.SplObject()
        system = lib.System(lib.Array(*parse_args(self.argv)), lib.CharArray(self.dir), self.encoding, self.in_out_err)
        natives = NativeInvokes()
        # native_graphics = gra.NativeGraphics()
        os_ = lib.Os()
        self.env.define_const("system", system, LINE_FILE)
        self.env.define_const("os", os_, LINE_FILE)
        self.env.define_const("natives", natives, LINE_FILE)

    def set_ast(self, ast_: ast.BlockStmt):
        """
        Sets up the abstract syntax tree to be interpreted.

        :param ast_: the root of the abstract syntax tree to be interpreted
        :return: None
        """
        self.ast = ast_

    def set_error_handler(self, handler):
        self.handler = handler

    def default_handler(self, e):
        error = traceback.format_exc()
        print_waring(self.env, error)
        return -1

    def interpret(self):
        """
        Starts the interpretation.

        :return: the exit value
        """
        try:
            return evaluate(self.ast, self.env)
        except Exception as e:
            return self.handler(e)


def parse_args(argv):
    """

    :param argv: the system argv
    :return: the argv in spl String object
    """
    return [lib.CharArray(x) for x in argv]


def add_natives(env: Environment):
    """
    Adds a bundle of global variables to the global scope.

    Includes all built-in functions and some global vars.

    :param env: the Environment
    :return: None
    """
    env.define_const("print", NativeFunction(print_, "print", True), LINE_FILE)
    env.define_const("println", NativeFunction(print_ln, "println", True), LINE_FILE)
    env.define_const("type", NativeFunction(typeof, "type"), LINE_FILE)
    env.define_const("pair", NativeFunction(lib.make_pair, "pair"), LINE_FILE)
    env.define_const("array", NativeFunction(lib.make_array, "array"), LINE_FILE)
    env.define_const("set", NativeFunction(lib.make_set, "set"), LINE_FILE)
    env.define_const("int", NativeFunction(lib.to_int, "int"), LINE_FILE)
    env.define_const("float", NativeFunction(lib.to_float, "float"), LINE_FILE)
    env.define_const("chars", NativeFunction(to_chars, "chars"), LINE_FILE)
    env.define_const("repr", NativeFunction(to_repr, "repr"), LINE_FILE)
    env.define_const("input", NativeFunction(input_, "input", True), LINE_FILE)
    env.define_const("f_open", NativeFunction(f_open, "f_open", True), LINE_FILE)
    env.define_const("eval", NativeFunction(eval_, "eval", True), LINE_FILE)
    env.define_const("dir", NativeFunction(dir_, "dir", True), LINE_FILE)
    env.define_const("get_env", NativeFunction(get_env, "get_env", True), LINE_FILE)
    env.define_const("get_cwf", NativeFunction(get_cwf, "get_cwf"), LINE_FILE)
    env.define_const("main", NativeFunction(is_main, "main", True), LINE_FILE)
    env.define_const("exit", NativeFunction(lib.exit_, "exit"), LINE_FILE)
    env.define_const("help", NativeFunction(help_, "help", True), LINE_FILE)
    env.define_const("exec", NativeFunction(exec_, "exec", True), LINE_FILE)
    env.define_const("id", NativeFunction(id_, "id"), LINE_FILE)

    env.define_const("Object", OBJECT, LINE_FILE)
    env.define_const("CharArray", lib.CharArray, LINE_FILE)
    env.define_const("Array", lib.Array, LINE_FILE)
    env.define_const("Pair", lib.Pair, LINE_FILE)
    env.define_const("Set", lib.Set, LINE_FILE)
    env.define_const("File", lib.File, LINE_FILE)
    env.define_const("Thread", Thread, LINE_FILE)
    env.define_const("System", lib.System, LINE_FILE)
    env.define_const("Os", lib.Os, LINE_FILE)
    env.define_const("Natives", NativeInvokes, LINE_FILE)
    env.define_const("Function", Function, LINE_FILE)
    env.define_const("Graphic", gra.Graphic, LINE_FILE)
    env.define_const("EnvWrapper", EnvWrapper, LINE_FILE)
    env.define_const("Class", Class, LINE_FILE)
    env.define_const("Module", Module, LINE_FILE)
    env.define_const("Annotation", Annotation, LINE_FILE)


class NativeFunction:
    def __init__(self, func: callable, name: str, need_env=False):
        self.name = name
        self.function: callable = func
        self.need_env = need_env

    def __str__(self):
        try:
            return "NativeFunction {}".format(self.function.__name__)
        except AttributeError:
            return ""

    def __repr__(self):
        return self.__str__()

    def call(self, env, args, kwargs):
        if self.need_env:
            if len(kwargs) > 0:
                return self.function(env, *args, **kwargs)
            else:
                return self.function(env, *args)
        else:
            if len(kwargs) > 0:
                return self.function(*args, **kwargs)
            else:
                return self.function(*args)


class ParameterPair:
    def __init__(self, name: str, preset):
        self.name: str = name
        self.preset = preset

    def __str__(self):
        return "{}={}".format(self.name, self.preset)

    def __repr__(self):
        return self.__str__()


class Function(lib.NativeType):
    """
    :type body: BlockStmt
    :type outer_scope: Environment
    """

    def __init__(self, params, body, outer, abstract: bool, annotations: lib.Set, doc):
        lib.NativeType.__init__(self)
        self.params: [ParameterPair] = params
        self.annotations = annotations
        self.body = body
        self.outer_scope = outer
        self.abstract = abstract
        self.doc = lib.CharArray(doc)
        self.file = None
        self.line_num = None
        self.clazz = None

    @classmethod
    def type_name__(cls) -> str:
        return "Function"

    def __str__(self):
        return "Function<{}>".format(id(self))

    def __repr__(self):
        return self.__str__()


class Class(lib.SplObject):
    def __init__(self, class_name: str, body: ast.BlockStmt, abstract: bool, superclasses: list,
                 outer_env: Environment, doc: str, line, file):
        lib.SplObject.__init__(self)
        self.class_name = class_name
        self.body = body
        self.superclasses: [Class] = superclasses
        self.outer_env = outer_env
        self.doc = lib.CharArray(doc)
        self.abstract = abstract
        # self.persists = ClassEnvironment(outer_env)
        self.line_num = line
        self.file = file

    @classmethod
    def type_name__(cls):
        return "Class"

    def __str__(self):
        if len(self.superclasses):
            return "Class<{}> extends {}".format(self.class_name, self.superclasses)
        else:
            return "Class<{}>".format(self.class_name)

    def __repr__(self):
        return self.__str__()


class EnvWrapper(lib.NativeType):

    def __init__(self, env: Environment):
        lib.NativeType.__init__(self)

        self.attrs = lib.Pair({})
        attrs = env.attributes()
        for key in attrs:
            self.attrs[lib.CharArray(key)] = attrs[key]

    @classmethod
    def type_name__(cls) -> str:
        return "EnvWrapper"

    def get(self, name):
        return self.attrs[name]

    def attributes(self):
        return self.attrs


class Thread(lib.NativeType):
    """
    An SPL thread object.
    """

    def __init__(self, process):
        lib.NativeType.__init__(self)

        self.process: multiprocessing.Process = process
        self.daemon = False

    @classmethod
    def type_name__(cls):
        return "Thread"

    def set_daemon(self, d):
        """
        Sets the daemon of this thread.

        If this thread is daemonic, it will end when the main program ends.

        :param d: the daemon value
        """
        self.daemon = d

    def start(self):
        """
        Starts this thread.
        """
        self.process.daemon = self.daemon
        self.process.start()

    def alive(self):
        return self.process.is_alive()


class NativeInvokes(lib.NativeType):
    """
    A class consists of static native invokes.
    """

    def __init__(self):
        lib.NativeType.__init__(self)

    @classmethod
    def type_name__(cls):
        return "Natives"

    @staticmethod
    def str_join(s: lib.CharArray, itr):
        """
        The native implementation of string join.

        :param s: the string
        :param itr: the iterable
        :return: the joined string
        """
        if isinstance(itr, lib.Iterable):
            return lib.CharArray(s.literal.join([x.literal for x in itr]))
        else:
            raise lib.TypeException("Object '{}': {} is not a native-iterable object.".format(typeof(itr), itr))

    @staticmethod
    def thread(env: Environment, target: Function, args: lib.Array):
        """
        Creates a new spl Thread.

        :param env: system default
        :param target: the target process
        :param args: arguments list
        :return: the new spl Thread
        """
        call = ast.FuncCall(LINE_FILE, target)
        call.args = ast.BlockStmt(LINE_FILE)
        for x in args.list:
            call.args.add_line(x)

        process = multiprocessing.Process(target=call_function, args=(call, target, env))
        return Thread(process)

    @staticmethod
    def log(x):
        """
        Returns the natural logarithm of x.

        :param x: the number to be calculated
        :return: the natural logarithm of x
        """
        return math.log(x)

    @staticmethod
    def pow(base, exp):
        """
        Returns the power of exp over base.

        :param base: the base number
        :param exp: the exponent
        :return: base ^ exp
        """
        return base ** exp

    @staticmethod
    def cos(rad):
        """
        Returns the cosine value of the angle, in radians

        :param rad: the angle, in radians
        :return: cos(rad)
        """
        return math.cos(rad)

    @staticmethod
    def asin(value):
        """
        Returns the arc sine angle of the value, in radians

        :param value: the sine value
        :return: asin(value), in radians
        """
        return math.asin(value)

    @staticmethod
    def atan(value):
        """
        Returns the arc tangent angle of the value, in radians

        :param value: the tangent value
        :return: atan(value), in radians
        """
        return math.atan(value)

    @staticmethod
    def variables(env: Environment):
        """
        Returns all variables of the nearest first-class scope, i.e. global scope or class scope.

        :param env: the calling scope
        :return: all variables of the nearest first-class scope
        """
        while not env.is_global() and not env.is_class():
            env = env.outer
        pair = lib.Pair({})
        for name in env.variables:
            pair.put(lib.CharArray(name), env.variables[name])
        return pair

    @staticmethod
    def constants(env: Environment):
        """
        Returns all constants of the nearest first-class scope, i.e. global scope or class scope.

        :param env: the calling scope
        :return: all constants of the nearest first-class scope
        """
        while not env.is_global() and not env.is_class():
            env = env.outer
        pair = lib.Pair({})
        for name in env.constants:
            pair.put(lib.CharArray(name), env.constants[name])
        return pair

    @staticmethod
    def locals(env: Environment):
        """
        Returns all variables and constants of this environment

        :param env:
        :return:
        """
        return env.attributes()


class ClassInstance(lib.SplObject):
    def __init__(self, env: Environment, class_name: str, clazz):
        """
        ===== Attributes =====
        :param class_name: name of this class
        :param clazz: the type of it
        :param env: instance attributes
        """
        lib.SplObject.__init__(self)
        self.clazz: Class = clazz
        self.class_name = class_name
        self.env = env
        self.env.constants["this"] = self

    def __getitem__(self, item):
        if self.env.contains_key("__getitem__"):
            call = ast.FuncCall(LINE_FILE, "__getitem__")
            call.args = ast.BlockStmt(LINE_FILE)
            call.args.add_line(item)
            return evaluate(call, self.env)
        else:
            raise lib.TypeException("{} object does not support indexing".format(self.class_name))

    def __hash__(self):
        if self.env.contains_key("__hash__"):
            call = ast.FuncCall(LINE_FILE, "__hash__")
            call.args = ast.BlockStmt(LINE_FILE)
            return evaluate(call, self.env)
        else:
            raise lib.TypeException("'{}' object is not hashable".format(self.class_name))

    def __neg__(self):
        if self.env.contains_key("__neg__"):
            call = ast.FuncCall(LINE_FILE, "__neg__")
            call.args = ast.BlockStmt(LINE_FILE)
            return evaluate(call, self.env)
        else:
            raise lib.TypeException("{} object has no neg attribute".format(self.class_name))

    def __repr__(self):
        if self.env.contains_key("__repr__"):
            func: Function = self.env.get("__repr__", LINE_FILE)
            result = call_function([], LINE_FILE, func, None)
            if result.class_name != "String":
                raise lib.TypeException("'__repr__' must return 'String' object")
            return result.env.get("lit", LINE_FILE).literal
        else:
            return "<{} at {}>".format(self.class_name, self.id)

    def __setitem__(self, item):
        if self.env.contains_key("__setitem__"):
            call = ast.FuncCall(LINE_FILE, "__setitem__")
            call.args = ast.BlockStmt(LINE_FILE)
            call.args.add_line(item)
            return evaluate(call, self.env)
        else:
            raise lib.TypeException("{} object does not support indexing".format(self.class_name))

    def __str__(self):
        if self.env.contains_key("__str__"):
            func: Function = self.env.get("__str__", LINE_FILE)
            result: ClassInstance = call_function([], LINE_FILE, func, None)
            if result.class_name != "String":
                raise lib.TypeException("'__str__' must return 'String' object")
            return result.env.get("lit", LINE_FILE).literal
        else:
            attr = self.env.attributes()
            attr.pop("this")
            return "<{} at {}>: {}".format(self.class_name, self.id, lib.make_pair(attr))

    def __int__(self):
        if self.class_name == "String":
            return int(self.env.get("lit", LINE_FILE).literal)
        else:
            raise lib.TypeException("Class '{}' cannot be convert to int".format(self.class_name))

    def __float__(self):
        if self.class_name == "String":
            return float(self.env.get("lit", LINE_FILE).literal)
        else:
            raise lib.TypeException("Class '{}' cannot be convert to float".format(self.class_name))


class Module(lib.SplObject):
    def __init__(self, module_env: ModuleEnvironment):
        lib.SplObject.__init__(self)

        self.env = module_env

    @classmethod
    def type_name__(cls):
        return "Module"


class SPLBaseException(Exception):
    def __init__(self, exception: ClassInstance):
        Exception.__init__(self, "SPLBaseException")

        self.exception = exception

    def __str__(self):
        return self.exception.__str__()

    def __repr__(self):
        return str(self)


# Native functions with dependencies

def to_chars(v) -> lib.CharArray:
    if isinstance(v, ClassInstance):
        return lib.CharArray(str(v))
    else:
        return lib.CharArray(v)


def to_repr(v) -> lib.CharArray:
    if isinstance(v, ClassInstance):
        return lib.CharArray(repr(v))
    else:
        return lib.CharArray(v)


def print_ln(env: Environment, s="", stream=None):
    """
    Prints out message to an output stream, with a new line at the end and the stream flushed.

    :param env: the calling environment
    :param s: the content to be printed, empty string as default
    :param stream: the output stream, stdout as default
    """
    if stream is None:
        stream = env.get_global_const("system").stdout
    print_(env, s, stream)
    print_(env, '\n', stream)
    flush: Function = stream.env.get("flush", LINE_FILE)
    call_function([], LINE_FILE, flush, env)


def print_(env: Environment, s, stream: ClassInstance = None):
    """
    Prints out message to an output stream.

    :param env: the calling environment
    :param s: the content to be printed
    :param stream: the output stream, stdout as default
    """
    # s2 = replace_bool_none(String(s).text__())
    if stream is None:
        stream = env.get_global_const("system").stdout
    write: Function = stream.env.get("write", LINE_FILE)
    call_function([lib.CharArray(s)], LINE_FILE, write, env)


def input_(env: Environment, prompt=lib.CharArray("")):
    """
    Asks input from user.

    This function will hold the program until the user inputs a new line character.

    :param env: the calling environment
    :param prompt: the prompt text to be shown to the user
    :return the user input, as <String>
    """
    system = env.get_global_const("system")
    print_(env, prompt, system.stdout)
    flush: Function = system.stdout.env.get("flush", LINE_FILE)
    call_function([], LINE_FILE, flush, env)

    readline: Function = system.stdin.env.get("readline", LINE_FILE)
    line = call_function([], LINE_FILE, readline, env)
    return lib.CharArray(line)


def typeof(obj) -> lib.CharArray:
    """
    Returns the type name of an object.

    :param obj: the object
    :return: the name of the type
    """
    if obj is None:
        return lib.CharArray("void")
    elif isinstance(obj, ClassInstance):
        return lib.CharArray(obj.class_name)
    elif isinstance(obj, bool):
        return lib.CharArray("boolean")
    elif isinstance(obj, lib.NativeType):
        return lib.CharArray(obj.type_name__())
    else:
        t = type(obj)
        return lib.CharArray(t.__name__)


def eval_(env: Environment, expr: lib.CharArray) -> ast.BlockStmt:
    """
    Evaluates a <String> as an expression.

    :param env: the environment
    :param expr: the string expression
    :return: the evaluation result
    """
    lexer = lex.Tokenizer()
    system = env.get("system", LINE_FILE)
    lexer.setup(script.get_spl_path(), system.argv[0].literal, system.argv[0].literal,
                import_lang=False)
    lexer.tokenize(str(expr).split('\n'))
    # print(lexer.tokens)
    parser = psr.Parser(lexer.get_tokens())
    block = parser.parse()
    # print(block)
    return block


def dir_(env: Environment, obj):
    """
    Returns a List containing all attributes of a type.

    :param env:
    :param obj: the object
    :return: a <List> of all attributes of a type.
    """
    lst = []
    if isinstance(obj, Class):
        mem.MEMORY.store_status()
        clazz: Class = env.get_class(obj.class_name)
        instance: ClassInstance = create_instance(clazz, env, clazz.outer_env)
        exc = {"this"}
        # for attr in instance.env.variables:
        for attr in instance.env.attributes():
            if attr not in exc:
                lst.append(attr)
        mem.MEMORY.restore_status()
    elif isinstance(obj, NativeFunction):
        for nt in lib.NativeType.__subclasses__():
            nt: lib.NativeType
            if nt.type_name__() == obj.name:
                lst.extend(dir(nt))
    elif isinstance(obj, type) and issubclass(obj, lib.NativeType):
        for nt in lib.NativeType.__subclasses__():
            if nt.type_name__() == obj.type_name__():
                lst.extend(dir(nt))
    else:
        raise lib.TypeException("No such type '{}'".format(typeof(obj)))
    lst.sort()
    return lib.Array(*lst)


def get_env(env: Environment, obj=None):
    if obj is None:
        return EnvWrapper(env)
    else:
        return EnvWrapper(obj.env)


def get_cwf(obj: str):
    """
    Returns the name of current working spl script.

    :param obj:
    :return: the name of current working spl script
    """
    return lib.CharArray(obj)


def is_main(env: Environment, obj):
    """
    Returns <true> iff the interpreter is working on the main script.

    :return: <true> iff the interpreter is working on the main script
    """
    return obj == env.get_global_const("system").argv[0].literal


def f_open(env: Environment, file: ClassInstance, mode: ClassInstance = None, encoding: ClassInstance = None):
    """
    Opens a file and returns the File object.

    :param env:
    :param file: the file's path, in <String>
    :param mode: the opening mode, 'r' as default
    :param encoding: the file's encoding, 'utf-8' as default
    :return: a reference to the File object
    """
    if mode is None:
        mode_s = "r"
    elif mode.class_name != "String":
        raise lib.TypeException("Unexpected type for argument")
    else:
        mode_s = mode.env.get("lit", LINE_FILE)
    if encoding is None:
        enc_s = "utf-8"
    elif encoding.class_name != "String":
        raise lib.TypeException("Unexpected type for argument")
    else:
        enc_s = encoding.env.get("lit", LINE_FILE)
    if file.class_name != "String":
        raise lib.TypeException("Unexpected type for argument")

    full_path = lib.concatenate_path(str(file), str(env.get_global_const("system").cwd))
    try:
        if "b" not in mode_s:
            f = open(full_path, str(mode), encoding=str(enc_s))
        else:
            f = open(full_path, str(mode))
        file = lib.File(f, str(mode))
        return file
    except IOError as e:
        return -1


def exec_(env: Environment, *args):
    path = str(env.get_global_const("system").cwd)
    if len(args) == 0:
        raise lib.ArgumentException("exec() takes at least one argument")
    elif len(args) == 1:
        if isinstance(args[0], lib.CharArray):
            line = str(args[0])
            return _exec_line(line, path)
        elif isinstance(args[0], lib.Array):
            line = " ".join(str(x) for x in args[0])
            return _exec_line(line, path)
        else:
            raise lib.TypeException("Unknown argument type of exec()")
    elif len(args) == 2:
        if isinstance(args[0], lib.CharArray) and isinstance(args[1], lib.Array):
            line = str(args[0]) + " " + " ".join(str(x) for x in args[1])
            return _exec_line(line, path)
        else:
            raise lib.TypeException("Unknown argument type of exec()")
    else:
        line = " ".join(str(x) for x in args)
        return _exec_line(line, path)


def id_(obj: lib.SplObject):
    return obj.id


def help_(env: Environment, obj=None):
    """
    Prints out the doc message of a function or a class.
    """
    if obj is None:
        print_ln(env, "Usage: help(obj)")
    elif isinstance(obj, NativeFunction):
        print_ln(env, "========== Help on native function ==========")
        print_ln(env, "function {}({})".format(obj.name, "(*args, **kwargs):"))
        print_ln(env, obj.function.__doc__)
        print_ln(env, "========== End of help ==========")
    elif isinstance(obj, type) and issubclass(obj, lib.NativeType):
        print_ln(env, "========== Help on native object ==========")
        print_ln(env, obj.doc__())
        print_ln(env, "========== End of help ==========")
    elif isinstance(obj, Function):
        print_ln(env, "========== Help on function ==========")
        print_ln(env, _get_func_title(obj))
        print_ln(env, _get_func_doc(obj))
        print_ln(env, "========== End of help ==========")
    elif isinstance(obj, Module):
        print_ln(env, "========== Help on Module ==========")
        print_ln(env, "Module object at <{}>".format(obj.id))
        print_ln(env, "========== End of help ==========")
    elif isinstance(obj, Class):
        print_ln(env, "========== Help on function ==========")
        class_doc = _get_class_doc(obj)
        print_ln(env, class_doc)
        print_ln(env, "---------- Methods ----------")

        mem.MEMORY.store_status()
        clazz: Class = env.get_class(obj.class_name)
        instance: ClassInstance = create_instance(clazz, env, clazz.outer_env)
        for attr_name in instance.env.attributes():
            if attr_name != "this":
                attr = instance.env.get(attr_name, (0, "help"))
                if isinstance(attr, Function):
                    print_ln(env, "   " + _get_func_title(attr, attr_name))
                    print_ln(env, _get_func_doc(attr))
                elif isinstance(attr, ast.AssignmentNode):
                    print_ln(env, "   " + attr_name)
                # print(_get_doc(instance.env.get(attr, (0, "help"))))
        mem.MEMORY.restore_status()
        print_ln(env, "========== End of help ==========")
    else:
        print_ln(env, "help() can only be used for classes, functions, native types, or native functions.")


# helper functions


def print_waring(env: Environment, msg: str):
    print_ln(env, msg, env.get_global_const("system").stderr)


def _get_class_doc(clazz: Class) -> str:
    doc = ["class ", clazz.class_name]
    if len(clazz.superclasses) > 0:
        doc.append(" extends ")
        for x in clazz.superclasses:
            # x: Class
            doc.append(x.class_name)
            doc.append(", ")
        doc.pop()
    doc.append(":\n")
    doc.append(clazz.doc.literal)
    return "".join(doc)


def _get_func_title(func: Function, name="") -> str:
    doc = ["function ", name, "("]
    for pp in func.params:
        if pp.preset is INVALID:
            doc.append(pp.name)
        else:
            doc.append("{}={}".format(pp.name, lib.replace_bool_none(str(pp.preset))))
        doc.append(", ")
    if len(func.params) > 0:
        doc.pop()
    doc.append("):")
    return "".join(doc)


def _get_func_doc(func: Function) -> str:
    return func.doc.literal


def _exec_line(line: str, path: str):
    cwd = os.getcwd()
    os.chdir(path)
    result = subprocess.call(line)
    os.chdir(cwd)
    return result


def _run_spl_script(env: Environment, path: lib.CharArray):
    spl_path = script.get_spl_path() + os.sep + script.SPL_NAME
    cmd = "python {} {}".format(spl_path, path)
    return exec_(env, lib.CharArray(cmd))


# Interpreter


def eval_for_loop(node: ast.ForLoopStmt, env: Environment):
    con: ast.BlockStmt = node.condition
    start = con.lines[0]
    end = con.lines[1]
    step = con.lines[2]

    title_scope = LoopEnvironment(env)
    block_scope = SubEnvironment(title_scope)

    result = evaluate(start, title_scope)

    step_type = step.node_type
    if step_type == ast.IN_DECREMENT_OPERATOR and not step.is_post:
        while not title_scope.broken and evaluate(end, title_scope):
            block_scope.invalidate()
            evaluate(step, title_scope)
            result = evaluate(node.body, block_scope)
            title_scope.resume_loop()
    else:
        while not title_scope.broken and evaluate(end, title_scope):
            block_scope.invalidate()
            result = evaluate(node.body, block_scope)
            title_scope.resume_loop()
            evaluate(step, title_scope)

    del title_scope
    del block_scope
    return result


def loop_spl_iterator(iterator: ClassInstance, invariant: str, body: ast.Node,
                      title_scope: LoopEnvironment, block_scope: SubEnvironment, lf: tuple):
    next_func = iterator.env.get("__next__", lf)
    has_next_func = iterator.env.get("__more__", lf)
    result = None
    while not title_scope.broken:
        block_scope.invalidate()
        has_next = call_function([], lf, has_next_func, title_scope)
        if has_next:
            next_call_res = call_function([], lf, next_func, title_scope)
            block_scope.assign(invariant, next_call_res, lf)
            result = evaluate(body, block_scope)
            title_scope.resume_loop()
        else:
            break
    del title_scope
    del block_scope
    return result


def eval_for_each_loop(node: ast.ForLoopStmt, env: Environment):
    con: ast.BlockStmt = node.condition
    inv: ast.Node = con.lines[0]
    lf = node.line_num, node.file

    title_scope = LoopEnvironment(env)

    block_scope = SubEnvironment(title_scope)

    if inv.node_type == ast.NAME_NODE:
        inv: ast.NameNode
        invariant = inv.name
    elif inv.node_type == ast.ASSIGNMENT_NODE:
        inv: ast.AssignmentNode
        evaluate(inv, title_scope)
        invariant = inv.left.name
    else:
        raise lib.SplException("Unknown type for for-each loop invariant")
    target = con.lines[1]
    # print(target)
    iterable = evaluate(target, title_scope)
    return iterate(iterable, invariant, node, title_scope, block_scope, env, lf)


def iterate(iterable, invariant, node, title_scope, block_scope, env, lf):
    if isinstance(iterable, lib.Iterable):
        result = None
        for x in iterable:
            block_scope.invalidate()
            block_scope.assign(invariant, x, lf)
            result = evaluate(node.body, block_scope)
            title_scope.resume_loop()
            if title_scope.broken:
                break
        del title_scope
        del block_scope
        # env.broken = False
        return result
    elif isinstance(iterable, ClassInstance):
        if is_subclass_of(iterable.clazz, env.get_class("Iterator")):
            return loop_spl_iterator(iterable, invariant, node.body, title_scope, block_scope, lf)
        elif is_subclass_of(iterable.clazz, env.get_class("Iterable")):
            iter_func = iterable.env.get("__iter__", lf)
            iterator: ClassInstance = call_function([], lf, iter_func, title_scope)
            return iterate(iterator, invariant, node, title_scope, block_scope, env, lf)
            # return loop_spl_iterator(iterator, invariant, node.body, title_scope, block_scope, lf)
    raise lib.SplException(
        "For-each loop on non-iterable objects, in {}, at line {}".format(node.file, node.line_num))


def eval_try_catch(node: ast.TryStmt, env: Environment):
    try:
        block_scope = SubEnvironment(env)
        result = evaluate(node.try_block, block_scope)
        return result
    except SPLBaseException as re:  # catches the exceptions thrown by SPL program
        block_scope = SubEnvironment(env)
        exception: ClassInstance = re.exception
        exception_class = exception.clazz
        spl_base_exception: Class = env.get_class("Exception")
        catches = node.catch_blocks
        for cat in catches:  # catch blocks
            block_scope.invalidate()
            for line in cat.condition.lines:
                if isinstance(line, ast.BinaryOperator) and line.operation == ":":
                    block_scope.define_var(line.left.name, exception, (line.line_num, line.file))
                    try:
                        catching_exception = evaluate(line.right, env)
                        if isinstance(catching_exception, Class):  # Catching the spl exception
                            if not is_subclass_of(catching_exception, spl_base_exception):
                                raise lib.TypeException(
                                    "Catching exception must derive from 'Exception', in file '{}', at line {}"
                                        .format(line.file, line.line_num))
                            if is_subclass_of(exception_class, catching_exception):
                                result = evaluate(cat.then, block_scope)
                                return result
                    except lib.NameException:
                        # not impossible for catching a python exception here
                        pass
                else:
                    raise lib.SplException("Unexpected content inside catch statement, in file '{}', at line {}"
                                           .format(line.file, line.operation))
        raise re
    except Exception as e:  # catches the exceptions raised by python
        block_scope = SubEnvironment(env)
        catches = node.catch_blocks
        for cat in catches:
            block_scope.invalidate()
            for line in cat.condition.lines:
                if isinstance(line, ast.BinaryOperator) and line.operation == ":":
                    block_scope.define_var(line.left.name, e, (line.line_num, line.file))
                    if isinstance(line.right, ast.NameNode):
                        catch_name = line.right.name
                        # catch_name = evaluate(line.right, env)
                        if catch_name == "Exception":
                            result = evaluate(cat.then, block_scope)
                            return result
                        elif catch_name == type(e).__name__:
                            result = evaluate(cat.then, block_scope)
                            return result
                else:
                    raise lib.SplException("Unexpected content inside catch statement, in file '{}', at line {}"
                                           .format(line.file, line.operation))
        raise e
    finally:
        block_scope = SubEnvironment(env)
        if node.finally_block is not None:
            return evaluate(node.finally_block, block_scope)


def is_subclass_of(child_class: Class, target_class: Class) -> bool:
    """
    Returns whether the child class is the ancestor class itself or inherited from that class.

    :param child_class: the child class to be check
    :param target_class: the ancestor class
    :return: whether the child class is the ancestor class itself or inherited from that class
    """
    if isinstance(child_class, Class):
        if child_class is target_class:
            return True
        else:
            return any([is_subclass_of(ccn, target_class) for ccn in child_class.superclasses])
    else:
        return False


def eval_operator(node: ast.BinaryOperator, env: Environment):
    left = evaluate(node.left, env)
    if node.assignment:
        right = evaluate(node.right, env)
        symbol = node.operation[:-1]
        res = arithmetic(left, right, symbol, env)
        return assignment(node.left, res, env, ast.ASSIGN)
    else:
        symbol = node.operation
        right_node = node.right
        return arithmetic(left, right_node, symbol, env)


def eval_braces(node: ast.BlockStmt, env: Environment) -> object:
    if len(node.lines) > 0:
        first = node.lines[0]
        if isinstance(first, ast.AssignmentNode):  # this is a pair
            result = lib.Pair({})
            for ass in node.lines:
                key = evaluate(ass.left, env)
                value = evaluate(ass.right, env)
                result.put(key, value)
        else:
            result = lib.Set()
            for n in node.lines:
                value = evaluate(n, env)
                result.add(value)
        return result
    else:
        return lib.Pair({})


def eval_assignment_node(node: ast.AssignmentNode, env: Environment):
    key = node.left
    value = evaluate(node.right, env)
    return assignment(key, value, env, node.level)


def assignment(key: ast.Node, value, env: Environment, level):
    t = key.node_type
    lf = key.line_num, key.file
    # print(key, value, level)
    if t == ast.NAME_NODE:
        key: ast.NameNode
        if level == ast.ASSIGN:
            env.assign(key.name, value, lf)
        elif level == ast.CONST:
            # var_type = generate_var_type(node.var_type, env)
            env.define_const(key.name, value, lf)
        elif level == ast.VAR:
            # var_type = generate_var_type(node.var_type, env)
            # print(value)
            env.define_var(key.name, value, lf)
        elif level == ast.FUNC_DEFINE:
            value: Function
            env.define_function(key.name, value, lf, value.annotations)
        else:
            raise lib.SplException("Unknown variable level")
        return value
    elif t == ast.DOT:
        key: ast.Dot
        if level == ast.CONST:
            raise lib.SplException("Unsolved syntax: assigning a constant to an instance")
        attr = key.right
        if isinstance(attr, ast.NameNode):
            name = attr.name
        else:
            raise lib.AttributeException("Attribute type '{}' cannot be set, in file '{}', at line {}"
                                         .format(typeof(attr), key.file, key.line_num))
        parent = evaluate(key.left, env)
        if isinstance(parent, ClassInstance) or isinstance(parent, Module):
            if level == ast.ASSIGN:
                parent.env.assign(name, value, lf)
            elif level == ast.VAR:
                parent.env.define_var(name, value, lf)
            elif level == ast.CONST:
                parent.env.define_const(name, value, lf)
            else:
                raise lib.SplException("Unknown variable level")
        else:
            raise lib.TypeException("Type '{}' does not support attribute assignment, in file '{}', at line {}"
                                    .format(typeof(parent), key.file, key.line_num))
        return value
    elif t == ast.INDEXING_NODE:  # setitem
        key: ast.IndexingNode
        return set_item(key.call_obj, key.arg, value, env)
    else:
        raise lib.InterpretException("Unknown assignment, in {}, at line {}".format(key.file, key.line_num))


def set_item(call_obj, index_node, value, env):
    obj = evaluate(call_obj, env)
    setitem_object = ast.NameNode(LINE_FILE, "__setitem__")
    arg_list = index_node.lines.copy()
    arg_list.append(value)
    if isinstance(obj, ClassInstance):
        return call_function(arg_list, LINE_FILE, obj.env.get("__setitem__", LINE_FILE), env)
    elif isinstance(obj, lib.NativeType):
        return native_types_call(obj, setitem_object, arg_list, env)
    else:
        raise lib.TypeException("Unknown type for index assignment")


def init_class(node: ast.Node, call_env: Environment, class_define_env=None):
    if class_define_env is None:
        class_define_env = call_env

    if isinstance(node, ast.NameNode):
        clazz = class_define_env.get_class(node.name)
        if isinstance(clazz, Class):
            return create_instance(clazz, call_env, class_define_env)
        elif issubclass(clazz, lib.NativeType):
            return create_native_instance(clazz, call_env)
        else:
            raise lib.TypeException("Unknown type to instantiate, int file '{}', at line {}"
                                    .format(node.file, node.line_num))
    elif isinstance(node, ast.FuncCall):
        clazz = evaluate(node.call_obj, class_define_env)
        if isinstance(clazz, Class):
            return create_instance(clazz, call_env, class_define_env, node)
        elif isinstance(clazz, Function):
            return create_instance(clazz.clazz, call_env, class_define_env, node)
        elif issubclass(clazz, lib.NativeType):
            return create_native_instance(clazz, call_env, node)
        else:
            raise lib.TypeException("Unknown type to instantiate, int file '{}', at line {}"
                                    .format(node.file, node.line_num))
    elif isinstance(node, ast.Dot):
        module = evaluate(node.left, class_define_env)
        return init_class(node.right, call_env, module.env)
    else:
        raise lib.TypeException("Could not create class instance of type '{}', in file '{}', at line {}"
                                .format(typeof(node), node.file, node.line_num))


def create_instance(clazz: Class, call_env: Environment, class_define_env: Environment,
                    call: ast.FuncCall = None):
    if clazz.abstract:
        raise lib.SplException("Abstract class is not instantiable")

    scope = ClassEnvironment(clazz.outer_env)
    # scope.extend_functions(clazz.persists)
    class_inheritance(clazz, class_define_env, scope)

    # print(scope.variables)
    instance = ClassInstance(scope, clazz.class_name, clazz)
    attrs = scope.attributes()
    for k in attrs:
        v = attrs[k]
        if isinstance(v, Function):
            v.outer_scope = scope
            v.clazz = clazz

    if call is not None:
        lf = call.line_num, call.file
        func: Function = scope.get(clazz.class_name, lf)
        args_list = make_arg_list(call)[1]
        call_function(args_list, lf, func, call_env)

    return instance


def create_native_instance(clazz: type, call_env: Environment, call: ast.FuncCall = None):
    if call is None:
        return clazz.__new__(clazz, None)
    else:
        call_obj, args = make_arg_list(call)
        pos_args, kwargs = parse_function_args(args, call_env)
        return clazz(*pos_args, **kwargs)


def make_arg_list(call: ast.FuncCall) -> (ast.Node, list):
    if call.args is None:
        raise lib.SplException("Argument of function '{}' not set, in file '{}', at line {}."
                               .format(call.call_obj, call.file, call.line_num))
    return call.call_obj, call.args.lines


def eval_eval(block: ast.BlockStmt, env: Environment):
    try:
        res = evaluate(block, env)
        return res
    except Exception:
        error = traceback.format_exc()
        print_waring(env, error)
        return -1


def eval_func_call(node: ast.FuncCall, env: Environment):
    lf = node.line_num, node.file
    func = evaluate(node.call_obj, env)
    call_obj, arg_list = make_arg_list(node)

    if isinstance(func, Function):
        result = call_function(arg_list, lf, func, env)
        return result
    elif isinstance(func, ClassInstance):
        constructor: Function = func.env.get(func.class_name, lf)
        call_function(arg_list, lf, constructor, env)  # call constructor
        return func
    elif isinstance(func, NativeFunction):
        args, kwargs = parse_function_args(node.args.lines, env)
        if func.name == "getcwf" or func.name == "main":
            args.append(node.file)
        result = func.call(env, args, kwargs)
        if isinstance(result, ast.BlockStmt):
            # Special case for "eval"
            return eval_eval(result, env)
        else:
            return result
    else:
        raise lib.InterpretException("Type '{}' is not a function call, in {}, at line {}."
                                     .format(typeof(func), node.file, node.line_num))


def parse_function_args(args: list, call_env: Environment) -> (list, dict):
    pos_args = []  # Positional arguments
    kwargs = {}  # Keyword arguments

    for arg in args:
        if isinstance(arg, ast.Node):
            lf = arg.line_num, arg.file
            if arg.node_type == ast.ASSIGNMENT_NODE:
                arg: ast.AssignmentNode
                kwargs[arg.left.name] = evaluate(arg.right, call_env)
            elif arg.node_type == ast.UNARY_OPERATOR:
                arg: ast.UnaryOperator
                if arg.operation == "unpack":
                    args_list: lib.Array = evaluate(arg.value, call_env)
                    proceed_unpack(args_list, pos_args, lf, call_env)
                elif arg.operation == "kw_unpack":
                    args_pair: lib.Pair = evaluate(arg.value, call_env)
                    proceed_kw_unpack(args_pair, kwargs, lf, call_env)
                elif arg.operation == "neg" or arg.operation == "new":
                    pos_args.append(evaluate(arg, call_env))
                else:
                    raise lib.TypeException("Invalid operator in function parameter, in file '{}', at line {}."
                                            .format(arg.file, arg.line_num))
            else:
                pos_args.append(evaluate(arg, call_env))
        else:
            pos_args.append(evaluate(arg, call_env))

    return pos_args, kwargs


def proceed_unpack(args_list, pos_args, lf, call_env):
    if isinstance(args_list, lib.Array):
        for an_arg in args_list:
            pos_args.append(an_arg)
    elif isinstance(args_list, ClassInstance):
        unpack = args_list.env.get("__unpack__", lf)
        res = call_function([], lf, unpack, call_env)
        proceed_unpack(res, pos_args, lf, call_env)
    else:
        raise lib.TypeException("Type '{}' does not support unpack operation, in file '{}', at line {}."
                                .format(typeof(args_list), lf[1], lf[0]))


def proceed_kw_unpack(args_pair, kwargs: dict, lf, call_env):
    # print(args_pair)
    if isinstance(args_pair, lib.Pair):
        for an_arg in args_pair:
            kwargs[an_arg.literal] = args_pair[an_arg]
    elif isinstance(args_pair, ClassInstance):
        kwu = args_pair.env.get("__kw_unpack__", lf)
        res = call_function([], lf, kwu, call_env)
        proceed_kw_unpack(res, kwargs, lf, call_env)
    else:
        raise lib.TypeException("Type '{}' does not support keyword unpack operation, in file '{}', at line {}."
                                .format(typeof(args_pair), lf[1], lf[0]))


def call_function(args: list, lf: tuple, func: Function, call_env: Environment):
    """
    Calls a function

    :param args: the arguments list
    :param lf: line and file of the caller
    :param func: the function object itself
    :param call_env: the environment where the function call was made
    :return: the function result
    """
    if not isinstance(func, Function):
        raise lib.TypeException("Type {} is not callable, in '{}', at line {}."
                                .format(typeof(func), lf[1], lf[0]))
    if func.abstract:
        raise lib.AbstractMethodException("Abstract method is not callable, in '{}', at line {}."
                                          .format(lf[1], lf[0]))

    scope = FunctionEnvironment(func.outer_scope)
    params = func.params

    pos_args, kwargs = parse_function_args(args, call_env)

    variable_length = False  # Whether there exists unpack arguments

    arg_index = 0
    for i in range(len(params)):  # Assigning function arguments
        param: ParameterPair = params[i]
        if param.preset is UNPACK_ARGUMENT:
            variable_length = True
            arg_index = call_unpack(param.name, pos_args, arg_index, scope, call_env, lf)
            continue
        elif param.preset is KW_UNPACK_ARGUMENT:
            variable_length = True
            call_kw_unpack(param.name, kwargs, scope, call_env, lf)
            continue
        elif i < len(pos_args):  # positional argument
            arg = pos_args[arg_index]
            arg_index += 1
        elif param.name in kwargs:
            arg = kwargs[param.name]
        elif param.preset is not INVALID:
            arg = param.preset
        else:
            raise lib.ArgumentException("Function at <{}> missing a positional argument '{}', in file '{}', at line {}"
                                        .format(func.id, param.name, lf[1], lf[0]))

        e = evaluate(arg, call_env)
        scope.define_var(param.name, e, lf)

    if not variable_length and len(pos_args) + len(kwargs) > len(params):
        raise lib.ArgumentException("Too many arguments for function at <{}>, in file '{}', at line {}"
                                    .format(func.id, lf[1], lf[0]))

    return evaluate(func.body, scope)


def call_unpack(name: str, pos_args: list, index, scope: Environment, call_env: Environment, lf) -> int:
    lst = []
    while index < len(pos_args):
        arg = pos_args[index]
        e = evaluate(arg, call_env)
        lst.append(e)
        index += 1

    spl_lst = lib.Array(*lst)
    scope.define_var(name, spl_lst, lf)
    return index


def call_kw_unpack(name: str, kwargs: dict, scope: Environment, call_env: Environment, lf):
    pair = lib.Pair({})
    for k in kwargs:
        v = kwargs[k]
        e = evaluate(v, call_env)
        pair[lib.CharArray(k)] = e

    scope.define_var(name, pair, lf)


def eval_dot(node: ast.Dot, env: Environment):
    instance = evaluate(node.left, env)
    obj = node.right
    t = obj.node_type
    lf = node.line_num, node.file
    # print(node.left)
    if t == ast.NAME_NODE:
        obj: ast.NameNode
        if isinstance(instance, lib.NativeType):
            return native_types_attr_invoke(instance, obj)
        elif isinstance(instance, ClassInstance) or isinstance(instance, Module):
            attr = instance.env.get(obj.name, lf)
            return attr
        else:
            # print(instance)
            raise lib.TypeException("Type '{}' does not have attribute '{}', in '{}', at line {}"
                                    .format(typeof(instance), obj.name, node.file, node.line_num))
    elif t == ast.FUNCTION_CALL:
        obj: ast.FuncCall
        call_obj, args = make_arg_list(obj)
        if isinstance(instance, lib.NativeType):
            try:
                return native_types_call(instance, call_obj, args, env)
            except IndexError as ie:
                raise lib.IndexOutOfRangeException(str(ie) + " in file: '{}', at line {}"
                                                   .format(node.file, node.line_num))
        elif isinstance(instance, ClassInstance) or isinstance(instance, Module):
            func = evaluate(obj.call_obj, instance.env)
            result = call_function(args, lf, func, env)
            return result
        else:
            raise lib.TypeException("Not a class instance; {} instead, in file '{}', at line {}"
                                    .format(typeof(instance), node.file, node.line_num))
    else:
        raise lib.InterpretException("Unknown Syntax, in file '{}', at line {}".format(node.file, node.line_num))


def get_node_in_annotation(node: ast.AnnotationNode, env: Environment, ann_list: list) -> (ast.Node, ast.Node):
    if node.args is not None:
        node.args.standalone = True
        content = evaluate(node.args, env)
    else:
        content = None
    ann = Annotation(lib.CharArray(node.name), content)
    ann_list.append(ann)
    if isinstance(node.body, ast.AssignmentNode):
        if isinstance(node.body.right, ast.DefStmt) and node.body.level == ast.FUNC_DEFINE:
            fn: ast.DefStmt = node.body.right
            fn.annotations = ann_list
            return node.body
    elif isinstance(node.body, ast.AnnotationNode):
        return get_node_in_annotation(node.body, env, ann_list)

    throw_spl_exception("AnnotationException", (node.line_num, node.file), env)


def arithmetic(left, right_node: ast.Node, symbol, env: Environment):
    if symbol in stl.LAZY:
        if left is None or isinstance(left, bool):
            return primitive_and_or(left, right_node, symbol, env)
        elif isinstance(left, int) or isinstance(left, float):
            return num_and_or(left, right_node, symbol, env)
        else:
            raise lib.InterpretException("Operator '||' '&&' do not support type.")
    else:
        right = evaluate(right_node, env)
        if left is None or isinstance(left, bool):
            return primitive_arithmetic(left, right, symbol)
        elif isinstance(left, int) or isinstance(left, float):
            return num_arithmetic(left, right, symbol)
        elif isinstance(left, lib.CharArray):
            return string_arithmetic(left, right, symbol)
        elif isinstance(left, lib.NativeType):  # NativeTypes other than String
            return native_arithmetic(left, right, symbol)
        elif isinstance(left, ClassInstance):
            return instance_arithmetic(left, right, symbol, env)
        elif isinstance(left, Class):
            return class_arithmetic(left, right, symbol, env, right_node)
        else:
            return raw_type_comparison(left, right, symbol)


def class_arithmetic(left: Class, right, symbol, env: Environment, right_node):
    if symbol == "===":
        return isinstance(right, Class) and left.id == right.id
    elif symbol == "!==":
        return not isinstance(right, Class) or left.id != right.id
    elif symbol == "subclassof":
        if isinstance(right, Class):
            return is_subclass_of(left, right)
        else:
            return False
    elif symbol == "instanceof":
        return isinstance(right_node, ast.NameNode) and right_node.name == "Class"
    else:
        raise lib.AttributeException("'Class' object does not support operation '{}'".format(left.class_name, symbol))


def instance_arithmetic(left: ClassInstance, right, symbol, env: Environment):
    if symbol == "===" or symbol == "is":
        return isinstance(right, ClassInstance) and left.id == right.id
    elif symbol == "!==":
        return not isinstance(right, ClassInstance) or left.id != right.id
    elif symbol == "instanceof":
        if isinstance(right, Class):
            return is_subclass_of(env.get_class(left.class_name), right)
        elif isinstance(right, Function):
            return is_subclass_of(env.get_class(left.class_name), right.clazz)
        else:
            return False
    else:
        op_name = "__" + stl.BINARY_OPERATORS[symbol] + "__"
        call_obj = ast.NameNode(LINE_FILE, op_name)
        if not left.env.contains_key(op_name):
            raise lib.AttributeException("Class '{}' does not support operation '{}'".format(left.class_name, symbol))
        func: Function = evaluate(call_obj, left.env)
        result = call_function([right], LINE_FILE, func, env)
        return result


def native_arithmetic(left: lib.NativeType, right, symbol: str):
    if symbol == "===" or symbol == "is":
        return isinstance(right, lib.NativeType) and left.id == right.id
    elif symbol == "!==":
        return not isinstance(right, lib.NativeType) or left.id != right.id
    elif symbol == "instanceof":
        if isinstance(right, NativeFunction):
            return left.type_name__() == right.name
        elif inspect.isclass(right):
            return left.type_name__() == right.type_name__()
        else:
            return False
    elif symbol == "==":
        return left == right
    elif symbol == "!=":
        return left != right
    else:
        raise lib.TypeException("Unsupported operation '{}' between {} and {}".format(symbol,
                                                                                      typeof(left),
                                                                                      typeof(right)))


STRING_ARITHMETIC_TABLE = {
    "==": lambda left, right: left == right,
    "!=": lambda left, right: left != right,
    "+": lambda left, right: left + right,
    "===": lambda left, right: left is right,
    "is": lambda left, right: left is right,
    "!==": lambda left, right: left is not right,
    "instanceof": lambda left, right: inspect.isclass(right) and right.type_name__() == "String"
}


def string_arithmetic(left, right, symbol):
    return STRING_ARITHMETIC_TABLE[symbol](left, right)


RAW_TYPE_COMPARISON_TABLE = {
    "==": lambda left, right: left == right,
    "!=": lambda left, right: left != right,
    "===": lambda left, right: left is right,
    "is": lambda left, right: left is right,
    "!==": lambda left, right: left is not right,
    "instanceof": lambda left, right: raw_type_instanceof(left, right),
}


def raw_type_instanceof(left, right):
    return isinstance(right, type) and isinstance(left, right)


def raw_type_comparison(left, right, symbol):
    return RAW_TYPE_COMPARISON_TABLE[symbol](left, right)


def primitive_and_or(left, right_node: ast.Node, symbol, env: Environment):
    if left:
        if symbol == "&&" or symbol == "and":
            right = evaluate(right_node, env)
            return right
        elif symbol == "||" or symbol == "or":
            return True
        else:
            raise lib.TypeException("Unsupported operation for primitive type")
    else:
        if symbol == "&&" or symbol == "and":
            return False
        elif symbol == "||" or symbol == "or":
            right = evaluate(right_node, env)
            return right
        else:
            raise lib.TypeException("Unsupported operation for primitive type")


PRIMITIVE_ARITHMETIC_TABLE = {
    "==": lambda left, right: left == right,
    "!=": lambda left, right: left != right,
    "===": lambda left, right: left is right,
    "is": lambda left, right: left is right,
    "!==": lambda left, right: left is not right,
    "instanceof": lambda left, right: isinstance(right, NativeFunction) and
                                      PRIMITIVE_TYPE_TABLE[right.name] == type(left).__name__
}


def primitive_arithmetic(left, right, symbol):
    operation = PRIMITIVE_ARITHMETIC_TABLE[symbol]
    return operation(left, right)


def num_and_or(left, right_node: ast.Node, symbol, env: Environment):
    if left:
        if symbol == "||" or symbol == "or":
            return True
        elif symbol == "&&" or symbol == "and":
            right = evaluate(right_node, env)
            return right
        else:
            raise lib.TypeException("No such symbol")
    else:
        if symbol == "&&" or symbol == "and":
            return False
        elif symbol == "||" or symbol == "or":
            right = evaluate(right_node, env)
            return right
        else:
            raise lib.TypeException("No such symbol")


def divide(a, b):
    if isinstance(a, int) and isinstance(b, int):
        return a // b
    else:
        return a / b


NUMBER_ARITHMETIC_TABLE = {
    "+": lambda left, right: left + right,
    "-": lambda left, right: left - right,
    "*": lambda left, right: left * right,
    "/": divide,  # a special case in case to produce integer if int/int
    "%": lambda left, right: left % right,
    "==": lambda left, right: left == right,
    "!=": lambda left, right: left != right,
    ">": lambda left, right: left > right,
    "<": lambda left, right: left < right,
    ">=": lambda left, right: left >= right,
    "<=": lambda left, right: left <= right,
    "<<": lambda left, right: left << right,
    ">>": lambda left, right: left >> right,
    "&": lambda left, right: left & right,
    "^": lambda left, right: left ^ right,
    "|": lambda left, right: left | right,
    "===": lambda left, right: left is right,
    "is": lambda left, right: left is right,
    "!==": lambda left, right: left is not right,
    "instanceof": lambda left, right: isinstance(right, NativeFunction) and right.name == type(left).__name__
}


def num_arithmetic(left, right, symbol):
    return NUMBER_ARITHMETIC_TABLE[symbol](left, right)


def is_def(node: ast.AssignmentNode):
    return isinstance(node.right, ast.DefStmt)


def class_inheritance(cla: Class, env: Environment, scope: Environment):
    """
    Instantiates all instance attributes in the class and its superclasses.

    :param cla:
    :param env: the class defined environment
    :param scope: the class scope
    :return: None
    """
    for sc in cla.superclasses:
        class_inheritance(sc, sc.outer_env, scope)

    # evaluate(cla.body, scope)
    for line in cla.body.lines:  # this step just fills the scope
        if isinstance(line, ast.AssignmentNode):
            value = evaluate(line.right, env)
            assignment(line.left, value, scope, line.level)
        elif isinstance(line, ast.AnnotationNode):
            # print(line)
            assign_node: ast.AssignmentNode = get_node_in_annotation(line, env, [])
            value = evaluate(assign_node.right, env)
            assignment(assign_node.left, value, scope, assign_node.level)
        else:
            raise lib.SplException("Not an expression inside class body")
            # evaluate(line, scope)


def native_types_call(instance: lib.NativeType, call_obj: ast.NameNode, arg_list: list, env: Environment):
    """
    Calls a method of a native object.

    :param instance: the NativeType object instance
    :param call_obj: the caller
    :param arg_list: the arguments list
    :param env: the current working environment
    :return: the returning value of the method called
    """
    args, kwargs = parse_function_args(arg_list, env)
    name = call_obj.name
    type_ = type(instance)
    # print(type_, name)
    method = getattr(type_, name)
    params: tuple = method.__code__.co_varnames
    if "self" in params and params.index("self") == 0:
        if "env" in params and params.index("env") == 1:
            res = method(instance, env, *args, **kwargs)
        else:
            res = method(instance, *args, **kwargs)
    else:
        if "env" in params and params.index("env") == 0:
            res = method(env, *args, **kwargs)
        else:
            res = method(*args, **kwargs)
    return res


def native_types_attr_invoke(instance: lib.NativeType, node: ast.NameNode):
    """
    Invokes an attribute of a native type.

    :param instance:
    :param node:
    :return:
    """
    name = node.name
    try:
        res = getattr(instance, name)
        return res
    except AttributeError:
        raise lib.AttributeException("'{}' object has no attribute '{}', in file '{}', at line {}"
                                     .format(instance.type_name__(), name, node.file, node.line_num))


def self_return(node):
    return node


def eval_return(node: ast.Node, env: Environment):
    res = evaluate(node, env)
    # print(env.variables)
    env.terminate(res)
    return res


def eval_block(node: ast.BlockStmt, env: Environment):
    if node.standalone:
        return eval_braces(node, env)
    else:
        result = None
        for line in node.lines:
            result = evaluate(line, env)
        return result


def eval_if_stmt(node: ast.IfStmt, env: Environment):
    cond = evaluate(node.condition, env)
    block_scope = SubEnvironment(env)
    if cond:
        return evaluate(node.then_block, block_scope)
    else:
        return evaluate(node.else_block, block_scope)


def eval_while(node: ast.WhileStmt, env: Environment):
    title_scope = LoopEnvironment(env)

    block_scope = SubEnvironment(title_scope)

    result = 0
    while not title_scope.broken and evaluate(node.condition, title_scope):
        block_scope.invalidate()
        result = evaluate(node.body, block_scope)
        title_scope.resume_loop()

    del title_scope
    del block_scope
    return result


def eval_for_loop_stmt(node: ast.ForLoopStmt, env: Environment):
    arg_num = len(node.condition.lines)
    if arg_num == 3:
        return eval_for_loop(node, env)
    elif arg_num == 2:
        return eval_for_each_loop(node, env)
    else:
        raise lib.ArgumentException("Wrong argument number for 'for' loop, in {}, at line {}"
                                    .format(node.file, node.line_num))


def eval_lambda(node: ast.LambdaExpression, env: Environment):
    if node.left.node_type == ast.NAME_NODE:
        pairs = [ParameterPair(node.left.name, INVALID)]
    elif node.left.node_type == ast.BLOCK_STMT:
        pairs = [ParameterPair(line.name, INVALID) for line in node.left.lines]
    else:
        raise lib.TypeException("Unexpected argument syntax for lambda expression, in file '{}', at line {}"
                                .format(node.file, node.line_num))
    f: Function = Function(pairs, node.right, env, False, lib.Set(), "")
    f.file = node.file
    f.line_num = node.line_num
    return f


def eval_anonymous_class(node: ast.AnonymousClass, env: Environment):
    if node.left.node_type == ast.UNARY_OPERATOR and node.left.operation == "new":
        stmt = node.left.value
        block: ast.BlockStmt = node.right
        block.standalone = False
        return create_anonymous_class(stmt, block, env)
    else:
        raise lib.TypeException("Unexpected usage of '<-' expression, in file '{}', at line {}"
                                .format(node.file, node.line_num))


def create_anonymous_class(node, block: ast.BlockStmt, call_env: Environment, superclass_defined_env=None):
    """
    :param node:
    :param block:
    :param call_env: the environment of calling, which is the same as the child class defined env in this case
    :param superclass_defined_env:
    :return:
    """
    if superclass_defined_env is None:
        superclass_defined_env = call_env

    if node.node_type == ast.NAME_NODE:
        superclass = superclass_defined_env.get_class(node.name)
        call = None
    elif node.node_type == ast.FUNCTION_CALL:
        superclass: Class = evaluate(node.call_obj, superclass_defined_env)
        call = node
    elif node.node_type == ast.DOT:
        module = evaluate(node.left, call_env)
        return create_anonymous_class(node.right, block, call_env, module.env)
    else:
        raise lib.TypeException("Unexpected usage of '<-' expression, in file '{}', at line {}"
                                .format(node.file, node.line_num))

    superclasses = [call_env.get_class("Object"), superclass]
    cla = Class("", block, False, superclasses, call_env,
                "", node.line_num, node.file)
    instance = create_instance(cla, call_env, superclass_defined_env, None)  # Function has different call mode

    if call is not None:
        lf = call.line_num, call.file
        func: Function = instance.env.get(superclass.class_name, lf)
        args_list = make_arg_list(call)[1]
        call_function(args_list, lf, func, call_env)

    return instance


def eval_def(node: ast.DefStmt, env: Environment):
    block: ast.BlockStmt = node.params
    params_lst = []
    for p in block.lines:
        # p: ast.Node
        if p.node_type == ast.NAME_NODE:
            p: ast.NameNode
            name = p.name
            value = INVALID
        elif p.node_type == ast.ASSIGNMENT_NODE:
            p: ast.AssignmentNode
            name = p.left.name
            value = evaluate(p.right, env)
        elif p.node_type == ast.UNARY_OPERATOR:
            p: ast.UnaryOperator
            if p.operation == "unpack":
                name = p.value.name
                value = UNPACK_ARGUMENT
            elif p.operation == "kw_unpack":
                name = p.value.name
                value = KW_UNPACK_ARGUMENT
            else:
                raise lib.SplException("Unexpected syntax in function parameter, in file '{}', at line {}."
                                       .format(node.file, node.line_num))
        else:
            raise lib.SplException("Unexpected syntax in function parameter, in file '{}', at line {}."
                                   .format(node.file, node.line_num))
        pair = ParameterPair(name, value)
        params_lst.append(pair)

    annotations = lib.Set()
    for ann in node.annotations:
        annotations.add(ann)
    f = Function(params_lst, node.body, env, node.abstract, annotations, node.doc)
    f.file = node.file
    f.line_num = node.line_num
    return f


def eval_class_stmt(node: ast.ClassStmt, env: Environment):
    superclasses = [evaluate(x, env) for x in node.superclass_nodes]
    cla = Class(node.class_name, node.block, node.abstract, superclasses, env,
                node.doc, node.line_num, node.file)
    env.define_var(node.class_name, cla, (node.line_num, node.file))
    return cla


def eval_assert(node: ast.Node, env: Environment):
    result = evaluate(node, env)
    if result is not True:
        lf = node.line_num, node.file
        throw_spl_exception("AssertionException", lf, env, [
            lib.CharArray("Assertion failed on expression '{}', in file '{}', at line {}"
                          .format(node, node.file, node.line_num))
        ])


def throw_spl_exception(name: str, lf, call_env: Environment, args: list = None):
    """
    Throws an exception defined in spl 'lib/lang.sp'

    :param name: the exception name
    :param lf: the line-file
    :param call_env: calling environment
    :param args: argument list, None if not calling constructor
    :return:
    """
    exception_class: Class = call_env.get_class(name)
    if args is None:
        instance = create_instance(exception_class, exception_class.outer_env, call_env)
    else:
        call = ast.FuncCall(lf, ast.NameNode(lf, exception_class))
        call.args = ast.BlockStmt(lf)
        call.args.lines = args
        instance = create_instance(exception_class, exception_class.outer_env, call_env, call)
    raise_exception(SPLBaseException(instance), call_env)


def eval_namespace(node: ast.Node, env: Environment):
    module: Module = evaluate(node, env)
    env.add_namespace(module.env)
    for ns in module.env.namespaces:
        env.add_namespace(ns)


HARD_UNARY_TABLE = {
    "return": eval_return,
    "throw": lambda n, env: raise_exception(SPLBaseException(evaluate(n, env)), env),
    "new": init_class,
    "assert": eval_assert,
    "namespace": eval_namespace
}

UNARY_TABLE = {
    "neg": lambda x: -x,
    "!": lambda x: not bool(x),
}


def eval_unary_expression(node: ast.UnaryOperator, env: Environment):
    t = node.operation
    if t in HARD_UNARY_TABLE:
        op = HARD_UNARY_TABLE[t]
        return op(node.value, env)
    else:
        value = evaluate(node.value, env)
        if isinstance(value, ClassInstance):
            op_name = "__" + stl.UNARY_OPERATORS[t] + "__"
            call_obj = ast.NameNode(LINE_FILE, op_name)
            if not value.env.contains_key(op_name):
                raise lib.AttributeException(
                    "Class '{}' does not support operation '{}'".format(value.class_name, t))
            # func: Function = left.env.get(fc.f_name, LINE_FILE)
            func: Function = evaluate(call_obj, value.env)
            result = call_function([], LINE_FILE, func, env)
            return result
        elif isinstance(value, lib.NativeType):
            op_name = "__" + stl.UNARY_OPERATORS[t] + "__"
            call_obj = ast.NameNode(LINE_FILE, op_name)
            result = native_types_call(value, call_obj, [], env)
            return result
        else:
            op = UNARY_TABLE[t]
            return op(value)


def eval_conditional_operator(left: ast.Node, mid: ast.Node, right: ast.Node, env: Environment):
    cond = evaluate(left, env)
    return evaluate(mid, env) if cond else evaluate(right, env)


TERNARY_TABLE = {
    ("?", ":"): eval_conditional_operator
}


def eval_ternary_expression(node: ast.TernaryOperator, env: Environment):
    op1 = node.first_op
    op2 = node.second_op
    op = TERNARY_TABLE[(op1, op2)]
    return op(node.left, node.mid, node.right, env)


INCREMENT_TABLE = {
    int: lambda n: n + 1,
}

DECREMENT_TABLE = {
    int: lambda n: n - 1
}


def eval_increment_decrement(node: ast.InDecrementOperator, env: Environment):
    current = evaluate(node.value, env)
    if node.operation == "++":
        f = INCREMENT_TABLE[type(current)]
    elif node.operation == "--":
        f = DECREMENT_TABLE[type(current)]
    else:
        raise lib.SplException("No such operator '{}'".format(node.operation))

    post_val = f(current)
    assignment(node.value, post_val, env, ast.ASSIGN)
    if node.is_post:
        return current
    else:
        return post_val


def eval_indexing_node(node: ast.IndexingNode, env: Environment):
    obj = evaluate(node.call_obj, env)
    call_obj = ast.NameNode(LINE_FILE, "__getitem__")

    if isinstance(obj, ClassInstance):
        return call_function(node.arg.lines, LINE_FILE, obj.env.get("__getitem__", LINE_FILE), env)
    elif isinstance(obj, lib.NativeType):
        return native_types_call(obj, call_obj, node.arg.lines, env)
    else:
        raise lib.TypeException("Unknown type for indexing")


def eval_import_node(node: ast.ImportNode, env: Environment):
    block = node.block
    path = node.path
    global_env: GlobalEnvironment = env.get_global()
    prev_module = global_env.find_module(path)

    lst = node.import_name.split(".")
    outer = env
    module = None
    for i in range(len(lst)):
        module_env = ModuleEnvironment(outer)
        module = Module(module_env)
        if i == len(lst) - 1:
            if prev_module is None:
                evaluate(block, module_env)
                global_env.add_module(path, module)
            else:
                module = prev_module

        outer.define_var(lst[i], module, LINE_FILE)
        outer = module_env
    return module


def raise_exception(e: SPLBaseException, env: Environment):
    if not is_subclass_of(env.get_class(e.exception.class_name), env.get_class("Exception")):
        raise lib.TypeException("Type '{}' is not throwable".format(e.exception.class_name))
    raise e


def eval_ann_node(node: ast.AnnotationNode, env: Environment):
    assign_node = get_node_in_annotation(node, env, [])
    return evaluate(assign_node, env)


# Operation table of every non-abstract node types
NODE_TABLE = {
    ast.LITERAL_NODE: lambda n, env: lib.CharArray(n.literal),
    ast.NAME_NODE: lambda n, env: env.get(n.name, (n.line_num, n.file)),
    ast.BREAK_STMT: lambda n, env: env.break_loop(),
    ast.CONTINUE_STMT: lambda n, env: env.pause_loop(),
    ast.ASSIGNMENT_NODE: eval_assignment_node,
    ast.DOT: eval_dot,
    ast.BINARY_OPERATOR: eval_operator,
    ast.UNARY_OPERATOR: eval_unary_expression,
    ast.TERNARY_OPERATOR: eval_ternary_expression,
    ast.BLOCK_STMT: eval_block,
    ast.IF_STMT: eval_if_stmt,
    ast.WHILE_STMT: eval_while,
    ast.FOR_LOOP_STMT: eval_for_loop_stmt,
    ast.DEF_STMT: eval_def,
    ast.FUNCTION_CALL: eval_func_call,
    ast.CLASS_STMT: eval_class_stmt,
    ast.TRY_STMT: eval_try_catch,
    ast.UNDEFINED_NODE: lambda n, env: UNDEFINED,
    ast.IN_DECREMENT_OPERATOR: eval_increment_decrement,
    ast.INDEXING_NODE: eval_indexing_node,
    ast.IMPORT_NODE: eval_import_node,
    ast.ANNOTATION_NODE: eval_ann_node,
    ast.LAMBDA_EXPRESSION: eval_lambda,
    ast.ANONYMOUS_CLASS: eval_anonymous_class
}


def evaluate(node: ast.Node, env: Environment):
    """
    Evaluates a abstract syntax tree node, with the corresponding working environment.

    :param node: the node in abstract syntax tree to be evaluated
    :param env: the working environment
    :return: the evaluation result
    """
    if env.is_terminated():
        return env.terminate_value()
    if env.is_broken_or_paused():
        return
    if isinstance(node, ast.Node):
        t = node.node_type
        node.execution += 1
        tn = NODE_TABLE[t]
        return tn(node, env)
    else:
        return node


# Processes before run


def string_run(self: lib.CharArray, env):
    result = _run_spl_script(env, self)
    return result


lib.CharArray.__run__ = string_run

OBJECT_DOC = """
The superclass of all spl object.
"""
OBJECT = Class("Object", ast.BlockStmt(LINE_FILE), True, [], None, OBJECT_DOC, *LINE_FILE)
