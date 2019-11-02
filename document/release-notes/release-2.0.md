# SPL 2.0 Release

Release date: 

## New Language Features

#### New syntax:
* Variable declaration and assignment via operator ":="
* Parenthesis around condition statements (`if`,`for`,`while`) and catch 
statement is no longer needed
* Braces around `if-else`, `while` body is required
* Keywords `function`, `def`, operators `and`, `or`, `not`, `is` are no
longer supported

#### Lambda Expressions:
* `x -> f(x)` for single parameter lambda expression
* `(arg1, arg2, ...) -> f(x)` for multiple parameters lambda expression

#### Anonymous Classes:
* Anonymous class creation and initialization via symbol `<-`. 
For example
```
var obj = new Object <- {
    ...
}
```

#### Spl Class String
* Implemented `String` in `lang.sp`, with `CharArray` in python
* Implemented `input` function in `lang.sp`, moved python based input
function into `natives`

#### Rework on Import System:
*  Syntax change of custom library importing: using path instead of 
package names. For example, `import "xx/yy/zz.sp"`
* The default import name is the file's name

#### Object Oriented Native Functions:
* Moved `f_open`, `exec`, `exit` into native class `os`

#### New native functions:
* `gc()` triggers garbage collection process manually
* `memory_view()` prints out memory items
* `memory_status()` prints out memory status

## SPL Memory Management System

#### Direct Memory Management:
* SPL now takes control of objects memory allocation
* Memory configurations in 'mem_configs.cfg'

#### Garbage Collector:


## Library Updates:

#### New Built-in Library:
* `stats.sp` Provides basic statistical functions

#### Library Function Updates:
* New library functions in `lang.sp`: `NonNullElse`, `round`
* All functions with arguments set `iter, function` in `functions.sp` 
now take the iterable as the first argument.
* More functions in `math.sp`
* Renamed all independent library function names in `lowerCamelCase`

## Optimizations:

#### Environment optimization:
* Removed the heap-variable in global scope
* Environment now stores only pointers

#### Operators:
* Adjusted operator precedences

## Key Feature Updates:

#### Even Slower

## Bug Fixes:
* Lines in a loop after `break` or `continue` still get executed (Since
1.5)
* The right side of "instanceof" not referencable in class itself
