from bin import spl_interpreter as inter
import bin.spl_lib as lib
from tkinter import filedialog
import tkinter
import tkinter.ttk


class Graphic(lib.NativeType):
    def __init__(self, name: lib.String, parent=None):
        lib.NativeType.__init__(self)

        if len(name.literal) > 4 and name.literal[:4] == "ttk.":
            true_func = getattr(tkinter.ttk, name.literal[4:])
        else:
            true_func = getattr(tkinter, name.literal)
        if parent is None:
            self.tk = true_func()
        else:
            self.tk = true_func(parent.tk)

    @classmethod
    def type_name__(cls) -> str:
        return "Graphic"

    def set_bg(self, color: lib.String):
        self.tk.configure(bg=color.literal)

    def configure(self, env, key: lib.String, value):
        v = proceed_function(value, env)
        cfg = {key.literal: v}
        self.tk.configure(cfg)

    def get(self, key: lib.String):
        return self.tk[key.literal]

    def set_attr(self, attr: lib.String, value):
        setattr(self.tk, attr.literal, value)

    def callback(self, env, cmd: lib.String, ftn):
        cfg = {cmd.literal: proceed_function(ftn, env)}
        self.tk.configure(cfg)

    @staticmethod
    def file_dialog(types: lib.Pair):
        res = filedialog.askopenfilename(filetypes=[(str(types[ext]), str(ext)) for ext in types])
        if res is not None:
            return lib.String(res)

    def call(self, env, func_name: lib.String, *args, **kwargs):
        func = getattr(self.tk, func_name.literal)
        args2 = []
        kwargs2 = {}
        for a in args:
            args2.append(proceed_function(a, env))
        for k in kwargs:
            kwargs2[str(k)] = proceed_function(kwargs[k], env)
        res = func(*args2, **kwargs2)
        if isinstance(res, str):
            return lib.String(res)
        else:
            return res


def proceed_function(ftn, env):
    if type(ftn).__name__ == "Function":
        return lambda: inter.call_function([], (0, "callback"), ftn, env)
    elif isinstance(ftn, lib.String):
        return str(ftn)
    elif isinstance(ftn, lib.Array):
        return ftn.list
    else:
        return ftn
