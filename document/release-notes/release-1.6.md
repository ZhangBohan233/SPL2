# SPL 1.6 Release

Release date: 2019/05/08

## New Features

#### New syntax:
* List creation with `[a, b, c]`
* Pair creation with `{a = x, b = y, c = z}`
* Set creation with `{a, b, c}`
* Array creation with `~[a, b, c]`
* New keywords `as` and `namespace`
* New binary operator `subclassof`
* Native types object creation via operator `new`
* `*args`, `**kwargs` now compatible for all types of function calls
* Complex expression support in function call arguments
* Constants in class now can be initialize in constructor function

#### New Import System:
* The `import` statement now imports a `Module` object, access via `.`
* Module name definition via `import *** as **`
* Namespace definition `namespace **`

#### New Iteration System:
* New superclass `lang.Iterator` which gives out a value every time the
`__next__` function is called
* `lang.Iterable.__iter__` now returns a `lang.Iterator`

#### New Native Functions:
* `exec()`
* `get_env()`
* `id()`

#### Library Updates:
* New library `lang.sp`, containing the most commonly used spl classes.
This library will be automatically imported unless the flag `-ni` is 
applied
* New library: SPL Graphics Library `sgl.sp`
* New library: JavaScript Object Notation support: `json.sp`
* New library: `util.sp`
* Merged `string_builder.sp` into `util.sp`
* Updated `unittest.sp`: added annotations `@RunBefore` and `@RunAfter`
* Implemented `List` in SPL, in `lang.sp`

#### Functional Updates:
* `system.stdin`, `system.stdout`, `system.stderr` now takes SPL 
`LineInputStream/OutputStream` objects, and can be set via SPL codes
* Errors are now print to `system.stderr`
* `Instance.clazz` attribute records the `Class` of it
* `*args` is now an array
* More runtime type check
* All classes with `__unpack__` defined can be used by unpack operator
`*`, `__kw_unpack__` for keyword unpack operator `**`
* Provided a python native way to throw an exception defined in 
`lang.sp`

#### Console Updates:
* A blank line will now break the continue line `...` in console

#### Other Updates:
* Changed the mechanism of parsing parenthesises
* Changed the mechanism of getitem and setitem
* Changed the mechanism of class extensions

## New Tools:
* SPL abstract syntax tree visualizer
* SPL IDLE
* Memory viewer

## Optimizations:
* SPL interpreter file structure optimization: Moved dependencies
into '/bin'

## Bugs Fixes:
* Some bugs in try-catch system
* Bugs in iteration system
* Parser might misidentify reserved names as function names
* Assignment for nested dot chain, for example 
`a.get_child().something = 1;`
* The bug that `eval(expr)` treats multiple lines as one line
