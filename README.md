# Mustiolo

Mustiolo is a lightweight Python framework for building command-line interfaces (CLI).
It allows to define commands, handle parameters, and provide user-friendly help messages with minimal effort. 
Mustiolo is designed to be simple, extensible, and easy to use.

![Alt text]https://github.com/Cereal84/mustiolo/images/mustiolo.png)

---

## Features

- **Command Registration**: Easily register commands using a decorator.
- **Parameter Handling**: Supports type annotations, default values, and mandatory parameters.
- **Help System**: Automatically generates help messages for commands and parameters.
- **Command History**: Handle the command history like Unix-like systems.
- **Autocomplete Command**: Command autocomplete via 'tab' key like Unix-like systems.
- **Error Handling**: Captures and displays errors in a user-friendly format.
- **Interactive CLI**: Provides an interactive prompt for executing commands.
- **Customizable Message Boxes**: Displays messages in visually appealing bordered boxes.

---

## Was there a need for another library?

No, there are a plenty number of libraries to build CLI applications in Python, this one
is an experiment to try to have the minimum code for building CLI applications.

It must be considered as a toy library just to experiment.


## Why this name ?

The 'mustiolo' is the smallest mammal in the world, weighing about 1.2-2.5 grams as an adult. 
It is present in Sardinia, in the Italian, Balkan, Iberian peninsulas and in North Africa.

This library aims to be the smallest library for building CLI applications in Python just like a mustiolo is the smallest mammal.

## Installation

To install Mustiolo, you can use pip:

```bash
git clone git@github.com:Cereal84/mustiolo.git
cd mustiolo
pip install .
```

## Basic usage

### Defining commands

Commands can be defined using the @command decorator. Each command can have a name, short help, and long help description.

```python
from mustiolo.cli import CLI

cli = CLI()

@cli.command()
def greet(name: str):
    """Greet a user by name."""
    print(f"Hello {name}!")

@cli.command()
def add(a: int, b: int):
    """Add two numbers and print the result."""
    print(f"The result is: {a + b}")

if __name__ == "__main__":
    cli.run()
```

Example of execution

```bash
> ?
greet    Greet a user by name.
add      Add two numbers and print the result.
> exit
```

It is possible to use the `?` command to see the usage of a specific command.

```bash
> ? add
Usage add Add two numbers and print the result.

add A B

Parameters:
		A	Type INTEGER [required]
		B	Type INTEGER [required]
> exit
```

## Override command informations

By default, the library uses as command name the function decorated via `@cli.command` and as short help message 
the `docstring`.
It is possible to override the information passing, in the decorator, the following arguments:

- name
- help_short
- help_long

So we can define a command like this:

```python
@cli.command(name="sum", help_short="Add two numbers", help_long="Add two numbers and print the result.")
def add(a: int, b: int):
    print(f"The result is: {a + b}")
```

In this example we override the command name and the short help message, but we keep the long help message as it is.

```bash
> ?
greet    Greet a user by name.
sum      Add two numbers
> ? sum
Usage sum Add two numbers and print the result.

sum A B

Parameters:
		A	Type INTEGER [required]
		B	Type INTEGER [required]
> 
```

## Mandatory and optional parameter/s

The library uses the annotation and type hint to understand if a parameter is a mandatory or optional.
If the argument in the function has a default value then the parameter in CLI command is optional, otherwise
it is mandatory.

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

## Configure CLI

The constructor of the `CLI` class accepts some parameters to configure the CLI behavior:
   - 'hello_message': A welcome message displayed when the CLI starts, default is empty.
   - 'prompt': The prompt string displayed to the user, default is ">".
   - 'autocomplete': A boolean to enable or disable command autocomplete, default is True.