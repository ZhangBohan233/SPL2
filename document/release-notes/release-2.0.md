# SPL 1.6 Release

Release date: 

## New Features

#### New syntax:
* Variable declaration and assignment via operator ":="
* Parenthesis around condition statements (`if`,`for`,`while`) and catch 
statement is no longer needed
* Braces around then block is required
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

#### Environment optimization:
* Removed the heap-variable in global scope

#### Library Function Updates:
* All functions with arguments set `iter, function` in `functions.sp` 
now take the iterable as the first argument.
