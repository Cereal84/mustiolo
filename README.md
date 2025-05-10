# TinyCLI

TinyCLI is a lightweight Python framework for building command-line interfaces (CLI).
It allows to define commands, handle parameters, and provide user-friendly help messages with minimal effort. 
TinyCLI is designed to be simple, extensible, and easy to use.

---

## Features

- **Command Registration**: Easily register commands using a decorator.
- **Parameter Handling**: Supports type annotations, default values, and mandatory parameters.
- **Help System**: Automatically generates help messages for commands and parameters.
- **Error Handling**: Captures and displays errors in a user-friendly format.
- **Interactive CLI**: Provides an interactive prompt for executing commands.
- **Customizable Message Boxes**: Displays messages in visually appealing bordered boxes.

---

## Was there a need for another library?

No, there are a plenty number of libraries to build CLI applications in Python, this one
is an experiment to try to have the minimum code for building CLI applications.

It must be considered as a toy library just to experiment.



## Basic usage

### Defining commands

Commands can be defined using the @command decorator. Each command can have a name, short help, and long help description.

```python
cli = TinyCLI()

@cli.command()
def greet(name: str = "World"):
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
Welcome to TinyCLI
> ?
greet    Greet a user by name.
add    Add two numbers and print the result.
> exit
```

It is possible to use the `?` command to see the usage of a specific command.

```bash
> ? greet
Usage greet Greet a user by name.

greet NAME

Parameters:
		NAME	Type STRING [optional] [default: World]
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
Welcome to TinyCLI
> ?
greet    Greet a user by name.
sum    Add two numbers
> ? sum
Usage sum Add two numbers and print the result.

sum A B

Parameters:
		A	Type INTEGER [required]
		B	Type INTEGER [required]
> 
```

