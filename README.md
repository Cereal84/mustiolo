# Mustiolo

Mustiolo is a lightweight Python framework for building command-line interfaces (CLI).
It allows you to define commands, handle parameters, and provide user-friendly help messages with minimal effort.
Mustiolo is designed to be simple, extensible, and easy to use.

![Logo](https://github.com/Cereal84/mustiolo/blob/main/image/mustiolo.png)

---

## Table of Contents

- [Mustiolo](#mustiolo)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Was there a need for another library?](#was-there-a-need-for-another-library)
  - [Why this name?](#why-this-name)
  - [Installation](#installation)
  - [Basic usage](#basic-usage)
    - [Defining commands](#defining-commands)
    - [Help format](#help-format)
  - [Override command information](#override-command-information)
    - [Notes](#notes)
      - [Menu](#menu)
      - [Usage](#usage)
  - [Mandatory and optional parameters](#mandatory-and-optional-parameters)
  - [Supported Types for Parameters](#supported-types-for-parameters)
  - [Group commands](#group-commands)
  - [Command Alias](#command-alias)
  - [Configure CLI](#configure-cli)
  - [License](#license)

---


## Features

- **Command Registration**: Easily register commands and subcommands using a decorator.
- **Parameter Handling**: Supports type annotations, default values, and mandatory parameters.
- **Help System**: Automatically generates help messages for commands and parameters.
- **Command History**: Handle the command history like Unix-like systems.
- **Autocomplete Command**: Command autocomplete via 'tab' key like Unix-like systems.
- **Error Handling**: Captures and displays errors in a user-friendly format.
- **Customizable Message Boxes**: Displays messages in visually appealing bordered boxes.

---

## Was there a need for another library?

No, there are a plenty number of libraries to build CLI applications in Python, this one
is an experiment to try to have the minimum code for building CLI applications.

It must be considered as a toy library just to experiment.


## Why this name?

The 'mustiolo' is the smallest mammal in the world, weighing about 1.2-2.5 grams as an adult. 
It is present in Sardinia, in the Italian, Balkan, Iberian peninsulas and in North Africa.

This library aims to be the smallest library for building CLI applications in Python just like a mustiolo is the smallest mammal.

## Installation

To install Mustiolo, you can use pip:


```bash
pip install mustiolo
```

or using the code in the repository:

```bash
git clone git@github.com:Cereal84/mustiolo.git
cd mustiolo
pip install .
```

## Basic usage

### Defining commands

Commands can be defined using the @command decorator. Each command can have a name, short help, and long help description.

### Help format
We've 2 types of 'help message':
 - **menu help**: the description which must be showed in the menu help.
 - **usage help**: is the command usage.

Help messages are retrieved by looking the docstring. 

```python
from mustiolo.cli import CLI

cli = CLI()

@cli.command()
def greet(name: str):
    """
    <menu>Greet a user by name.</menu>
    """
    
    print(f"Hello {name}!")

@cli.command()
def add(a: int, b: int):
    """
    <menu>Sum two numbers.</menu>
    <usage>Add two numbers and print the result.</usage>
    """
    
    print(f"The result is: {a + b}")

if __name__ == "__main__":
    cli.run()
```

Example of execution

```bash
> ?
greet    Greet a user by name.
add      Sum two numbers.
> exit
```

It is possible to use the `?` command to see the usage of a specific command.

```bash
> ? add
Add two numbers and print the result.

add A B

Parameters:
		A	Type INTEGER [required]
		B	Type INTEGER [required]
> exit
```

## Override command information

By default, the library uses as command name the function decorated via `@cli.command` and as short help message 
the `docstring`.
It is possible to override the information passing, in the decorator, the following arguments:

- name
- menu
- usage

So we can define a command like this:

```python
@cli.command(name="sum", menu="Add two numbers", usage="Add two numbers and print the result.")
def add(a: int, b: int):
    print(f"The result is: {a + b}")
```

In this example, we override the command name and the short help message, but we keep the long help message as it is.

```bash
> ?
greet    Greet a user by name.
sum      Add two numbers
> ? sum
Add two numbers and print the result.

sum A B

Parameters:
		A	Type INTEGER [required]
		B	Type INTEGER [required]
> 
```

### Notes


#### Menu
`menu` message is mandatory and can be specified via docstring or parameter in `command` decorator.
If both are void then an error will be returned.

#### Usage
`usage` works like `menu` and so it is possibile to be specified via docstring or decorator, but if none of them is
set then will be used the `menu` value.

The help message will be used in the following template

```bash
<usage message>

<command_name> <parameter1> ... <parameterN>

Parameters:
    <parameter1_name> <type> [<mandatory/optional>]
    ...
    <parameterN_name> <type> [<mandatory/optional>]
```

## Mandatory and optional parameters

The library uses annotations and type hints to determine if a parameter is mandatory or optional.
If the argument in the function has a default value, then the parameter in the CLI command is optional; otherwise, it is mandatory.

```python
@cli.command()
def greet(name: str = "World"):
    """Greet a user by name or print 'Hello World!'."""
    print(f"Hello {name}!")
```

```bash
> ? greet
Usage greet Greet a user by name or print 'Hello World!'.

greet NAME

Parameters:
		NAME	Type STRING [optional] [default: World]
```


## Supported Types for Parameters

Mustiolo automatically converts command-line arguments to the types declared in your function signatures. 
For this reason, type annotation is mandatory; otherwise, an error will be shown and the CLI will exit.
The following types are supported:

- **str**: No conversion is performed; the argument is passed as a string.
- **int**: The argument is converted to an integer.
- **float**: The argument is converted to a float.
- **bool**: Accepts `true`, `false`, `1`, `0` (case-insensitive). For example, `"true"` and `"1"` become `True`, `"false"` and `"0"` become `False`.
- **List (or `list`)**: Accepts a comma-separated string (e.g., `"a,b,c"` or `"1,2,3"`).  
  - If a subtype is specified (e.g., `List[int]`), each element is converted to that type.
  - Supported subtypes are: `str`, `int`, `float`, `bool`.
  - If no subtype is specified, elements are treated as strings.

**Examples:**

```python
@cli.command(menu="Example command", usage="An example command with various types.")
def example(a: int, b: float, c: bool, d: str, e: list, f: list[int]):
    print(a, b, c, d, e, f)
```

```bash
> example 5 3.14 true hello a,b,1 1,2,3
# Output: 5 3.14 True hello ['a', 'b', '1'] [1, 2, 3]
```

**Notes:**
- If the conversion fails (e.g., passing `"abc"` to an `int`), an error is shown.


## Group commands
It is possible to have a command tree specifyng a command group using `Menugroup` objects.
The group have a name that specify the command root.

```python
from mustiolo.cli import CLI, MenuGroup

from typing import List

cli = CLI()

# add the commands to the root menu
@cli.command()
def greet(name: str = "World"):
    """<menu>Greet a user by name.</menu>"""
    print(f"Hello {name}!")

math_submenu = MenuGroup("math", "Some math operations", "Some math operations")

@math_submenu.command()
def add(a: int, b: int):
    """
    <menu>Sum two numbers.</menu>
    <usage>Add two numbers and print the result.</usage>
    """
    print(f"The result is: {a + b}")

@math_submenu.command()
def add_list(numbers: List[int]):
    """<menu>Add N numbers.</menu>"""
    tot = sum(numbers)
    print(f"The result is: {tot}")

@math_submenu.command()
def sub(a: int, b: int):
    """<menu>Subtract two numbers.</menu>"""
    print(f"The result is: {a - b}")

# add math submenu to the root menu
cli.add_group(math_submenu)


if __name__ == "__main__":
    cli.run()
```

So we have four commands in the root menu, by default the root menu has '?' and 'exit', as 
you can see below:

 - ?
 - exit
 - greet
 - math

and math specify other commands:
 - add
 - add_list
 - sub

```bash
> ?
?    	Shows this help.
exit 	Exit the program
greet	Greet a user by name.
math    Some math operations
> ? math
add     	Add two numbers.
add_list	Add N numbers.
sub     	Subtract two numbers.

```

## Command Alias

It is possible to add alias to a command (not to a command group), you can do that in the
 `command` decorator.

```python

@cli.command(alias="names", menu="Shows a name list.")
def list_names():
    print(", ".join["Luca", "Mark", "Laura", "Watson"])

```

```bash

list_names, names	Shows a name list.

```

The autocomplete, if enabled, works on aliases too.

## Configure CLI

The constructor of the `CLI` class accepts some parameters to configure the CLI behavior:
   - 'hello_message': A welcome message displayed when the CLI starts, default is empty.
   - 'prompt': The prompt string displayed to the user, default is ">".
   - 'autocomplete': A boolean to enable or disable command autocomplete, default is True.


## License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.
