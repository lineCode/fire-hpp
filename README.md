
# Fire for C++

Fire for C++ is a library for creating a command line interface directly from function signature, inspired by [python-fire](https://github.com/google/python-fire). Here's a complete example of adding two numbers with a CLI:
 ```
#include <iostream>
#include <fire.hpp>

int fired_main(int x = fire::arg("x"), int y = fire::arg("y")) {
    std::cout << x + y << std::endl;
    return 0;
}

FIRE(fired_main)
```

That's it. And usage:

```
$ ./add -x=1 -y=2
3
```

As you likely expect,
* a meaningful help message is generated if prompted with `--help`, stating required arguments and their types.
* an error message is displayed for incorrect usage.

### What's covered?

All the standard stuff, like
* flags
* named and positional parameters
* required and optional parameters
* unlimited number of parameters
* conversions to integer, floating-point and `std::string`, with proper error reporting
* parameter descriptions
* typical constructs, such as expanding `-abc <=> -a -b -c` and `-x=1 <=> -x 1`

In addition, this library
* comes with thorough testing
* ~~works with Linux, Windows and Mac OS~~
* is a single header
* comes under very permissive [Boost licence](https://choosealicense.com/licenses/bsl-1.0/) (examples with [0-clause BSD](https://choosealicense.com/licenses/0bsd/))

### Requirements

* C++11 compatible compiler

Additionally for developing/testing:

* CMake 3.10+
* GTest
* Python 3.5+

## Q. Quick start

Let's go through parts of the above example and explain them one by one.

```
int fired_main(int x = fire::arg("x"), int y = fire::arg("y")) { // Define and convert arguments
    std::cout << x + y << std::endl; // Use x and y, they're ints.
    return 0; // Return value is passed to real main()
}

FIRE(fired_main) // Define real main(): parse arguments and call fired_main()
```

### <a id="quickfire"></a> Q.1 FIRE(fired_main)

Every program using Fire for C++ needs to have a `FIRE(...)` statement. This creates the program's entry point and _fires_ off your own "main" function. In a simplified form, the `FIRE(fired_main)` macro above expands to something like

```
int main(int argc, const char ** argv) {
    parse_arguments_and_store_into_static_variables(argc, argv);
    int return_code = fired_main();
    return return_code;
}
```

Note that `fired_main()` is called without arguments. As a result, default `fire::arg` objects are used, giving library the chance to assign correct values as arguments.

### Q.2 int fired_main(int x = fire::arg("x"), int y = fire::arg("y"))

This is your "main" function, called after parsing arguments in the actual main generated by Fire. The following requirements apply:
* all arguments are arithmetic, `std::string` or `std::vector` types
* all arguments are default-assigned with `fire::arg()` or `fire::arg::vector()` (Failing to do so results in bugs that are not reported by the library!)
* returns `int`

`fire::arg()` is actually a constructor that (obviously) returns a `fire::arg` object. This object gets implicitly converted to whatever type assigned. The converted values can of course be used in any way.

## D. Documentation

### D.1 FIRE(...) and FIRE_POSITIONAL(...)

See `FIRE(...)` [quick start](#quickfire).

`FIRE(...)` and `FIRE_POSITIONAL(...)` both create a main function to parse arguments and call `...`, however they differ in how arguments are parsed. `FIRE(...)` parses `program -x 1` as `program -x=1`, but `FIRE_POSITIONAL(...)` parses `-x` as a flag and `1` as a separate positional argument. Thus in order to use valued named arguments in positional mode, `-x=1` need to be used. There a two reasons:

* Mixing positional and named arguments with space separated values makes a bad CLI anyway, eg: `program a -x b c` doesn't seem like `-x=b` with `a` and `c` as positional.
* Implementing such CLI is likely impossible due to the Fire API.

### D.2 fire::arg(identifier[, description[, default_value]])

#### D.2.1 Identifier

Identifier used to find arguments from command line. Can either be
* `const char *`: named argument
    * Example: `int fired_main(int x = fire::arg("x"));`
    * CLI usage: `program -x=1`


* `initializer_list<const char *>`: named argument with a short-hand (single character) and long name
    * Example: `int fired_main(int x = fire::arg({"x", "long-name"}));`
    * CLI usage: `program -x=1`
    * CLI usage: `program --long-name=1`


* `int`: positional argument (requires [positional mode](#quickfire))
    * Example: `int fired_main(int x = fire::arg(0));`
    * CLI usage: `program 1`

#### D.2.2 Descrpition (optional)

`std::string` that gets printed when the program is prompted with `--help`.

* Example: `int fired_main(int x = fire::arg("x", "an argument"));`
* CLI usage: `program --help`
* Output:
```
    Usage:
      ./examples/basic -x=<INTEGER>


    Options:
      -x=<INTEGER>  an argument
```

#### D.2.3 Default value (optional)

Default value if no value is provided through command line. `std::string`, integral or floating point type. This default is also displayed in help page.

* Example: `int fired_main(int x = fire::arg("x", "", 0));`
* CLI usage: `program` -> `x=0`
* CLI usage: `program -x=1` -> `x=1`

### D.3 fire::arg conversions

In order to conveniently obtain parsed arguments and automatically check the validity of input, `fire::arg` class defines several implicit conversions.

#### D.3.1 std::string, integral, or floating point

Converts the argument value on command line to respective type. Displayes an error if conversion is impossible or default value is of wrong type.

* Example: `int fired_main(std::string name = fire::arg("name"));`
* CLI usage: `program --name=fire` -> `name="fire"`

#### D.3.2 fire::optional

Used for optional arguments without a reasonable default value. This way the default value doesn't get printed in a help message. The underlying type can be `std::string`, integral or floating point.

`fire::optional` is a tear-down version of [`std::optional`](https://en.cppreference.com/w/cpp/utility/optional), with compatible implementations for [`has_value()`](https://en.cppreference.com/w/cpp/utility/optional/operator_bool), [`value_or()`](https://en.cppreference.com/w/cpp/utility/optional/value_or) and [`value()`](https://en.cppreference.com/w/cpp/utility/optional/value).

* Example: `int fired_main(fire::optional<std::string> name = fire::arg("name"));`
* CLI usage: `program` -> `name.has_value()=false`
* CLI usage: `program --name="fire"` -> `name.has_value()=true` and `name.value()="fire"`

#### D.3.3 bool: flag argument

Boolean flags are `true` when they exist on command line and `false` when they don't. Multiple single-character flags can be packed on command line by prefixing with a single hyphen: `-abc <=> -a -b -c`

* Example: `int fired_main(bool flag = fire::arg("flag"));`
* CLI usage: `program` -> `flag=false`
* CLI usage: `program --flag` -> `flag=true`

### D.4 fire::arg::vector([description])

A method for getting all positional arguments (requires [positional mode](#quickfire)). The constructed object can be converted to `std::vector<std::string>`, `std::vector<integral type>` or `std::vector<floating point type>`. Description can be supplied for help message. Using `fire::arg::vector` forbids extracting positional arguments with `fire::arg(index)`.

* Example: `int fired_main(vector<std::string> params = fire::arg::vector());`
* CLI usage: `program abc xyz` -> `params={"abc", "xyz"}`
* CLI usage: `program` -> `params={}`

## Development

This library uses extensive testing. Unit tests are located in `tests/`, while `examples/` are used as integration tests. The latter also ensure examples are up-to-date. Before committing, please verify `./build/tests/run_all_tests.py` succeed.

All releases are currently tested on:
* Arch Linux gcc==10.1.0, clang==10.0.0: C++11, C++14, C++17 and C++20
* Ubuntu 18.04 clang=={3.9, 4.0}: C++11 and clang=={5.0, 6.0, 7.0, 8.0, 9.0}: C++11 and C++17
* Ubuntu 18.04 gcc=={5.5, 6.5, 7.5, 8.4}: C++11, C++14 and C++17

### TODO list:

#### Current state

* Test on Windows, Mac

#### v0.1 release

* Better error messages
    * Automatic testing for error messages
    * Improve CLI user errors
    * Improve API user errors
* Improve help messages
    * Refactor `log_elem::type` from `std::string` -> `enum class`
    * Help messages with better organization (separate positional arguments, named arguments, flags, etc. in `Usage` and descriptions)
    * Program description
* `super` keyword for `arg`, which will save program from exiting even if not all required arguments are present or correct (eg. for `--version`)
* Remove exceptions

#### v0.2 release

* Support for wide character strings
* Modules (with separate help messages for each module (otherwise impossible without exceptions))
