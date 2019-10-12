# SPL 1.5 Release

Release date: 2019/04/13

## New Features

#### New syntax:
* Increment and decrement operators `++` and `--`, supports for both
pre-execution and post-execution
* Ternary conditional operator `cond ? if_true : if_false`
* Assignment now be treated the same as any other binary expressions
* True anonymous call, operator `=>` is deprecated
* Packed arguments `*args` and keyword arguments `**kwargs`
* Run-time check using keyword `assert`
* Added text operators `and`, `or`, `not`, `is` to increase readability
* Duplicate variable name in different main scope is allowed

#### Multi-threading:
* SPL now supports simple multi-threading
    
#### Redesign the function calling:
* Function calls now do not rely on the function names.

#### Redesign parser:
* Better nested support
* More parse-time syntax check
    
#### Functionality augment:
* `StringBuilder.append` now returns the builder itself
* `String.format`
* `try-catch` now works on any type of exceptions
* Built-in functions `list()`, `set`, `pair` now take initial arguments
* All spl objects now extends `Object`

#### Help system:
* The help system is now implemented
* Use `help(something)` to check is document
    
#### Optimizations:
* Split the different type of environments, heavily reduced the code
inside a loop-environment
* Replaced the intermediate nodes of numbers, booleans, nulls by the
actual value
* Import optimization: the duplicate import will now not be executed
* Performance comparison: comparing to SPL 1.3:
    * Loops are 89% faster
    * Merge sort are 41% faster
    * Recursions are 19% slower

#### Bugs fixes:
* Exception caught is not accessible
* Long-existing bugs in id-allocated system
* Directly return an inner function inside function did not work
* Function `f_open` does not open the file with relative path

#### Others:
* Changed the format of command-line arguments
* Changed all reference type names to `UpperCamel`
