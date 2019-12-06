from bin import spl_interpreter as inter
import bin.spl_native_types as typ
import bin.spl_lib as lib
from tkinter import filedialog
import tkinter
import tkinter.ttk

GRA_LINE = 0, "graphic_lib"


class Graphic(lib.NativeType):
    def __init__(self, name, parent=None):
        lib.NativeType.__init__(self)

        name_cont: str = name.env.get("lit", GRA_LINE).literal
        if len(name_cont) > 4 and name_cont[:4] == "ttk.":
            true_func = getattr(tkinter.ttk, name_cont[4:])
        else:
            true_func = getattr(tkinter, name_cont)
        if parent is None:
            self.tk = true_func()
        else:
            self.tk = true_func(parent.tk)

    @classmethod
    def __type_name__(cls) -> str:
        return "Graphic"

    def set_bg(self, color):
        self.tk.configure(bg=color.env.get("lit", GRA_LINE).literal)

    def configure(self, env, key, value):
        v = proceed_function(value, env)
        cfg = {key.env.get("lit", GRA_LINE).literal: v}
        self.tk.configure(cfg)

    def get(self, key):
        return self.tk[key.env.get("lit", GRA_LINE).literal]

    def set_attr(self, attr, value):
        setattr(self.tk, attr.env.get("lit", GRA_LINE).literal, value)

    def callback(self, env, cmd, ftn):
        cfg = {cmd.env.get("lit", GRA_LINE).literal: proceed_function(ftn, env)}
        self.tk.configure(cfg)

    @staticmethod
    def file_dialog(types: typ.Pair):
        res = filedialog.askopenfilename(filetypes=[(str(types[ext]), str(ext)) for ext in types])
        if res is not None:
            return lib.CharArray(res)

    def call(self, env, func_name, *args, **kwargs):
        func = getattr(self.tk, func_name.env.get("lit", GRA_LINE).literal)
        args2 = []
        kwargs2 = {}
        for a in args:
            args2.append(proceed_function(a, env))
        for k in kwargs:
            kwargs2[str(k)] = proceed_function(kwargs[k], env)
        res = func(*args2, **kwargs2)
        if isinstance(res, str):
            return lib.CharArray(res)
        else:
            return res


def proceed_function(ftn, env):
    if type(ftn).__name__ == "Function":
        return lambda: inter.call_function([], (0, "callback"), ftn, env)
    elif isinstance(ftn, lib.CharArray):
        return str(ftn)
    elif isinstance(ftn, inter.ClassInstance):
        return str(ftn)
    elif isinstance(ftn, typ.Array):
        return ftn.as_py_list()
    else:
        return ftn
