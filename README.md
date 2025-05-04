# TinyCLI
TinyCLI is a toy library for building CLI applications.

There are a plenty number of libraries to build CLI applications in Python, this one
is an experiment to try to have the minimum code for building CLI applications.

It must be considered as a toy library just to experiment.

## Features

 - register commands via decorator,
 - automatic help message from docstrings,
 - specific command help message,
 - automatic check about command's parameters
     - required param
     - check on param type
 - custom error messages.


## Example

Here a minimum example about a CLI.

```python
from main import TinyCLI

cli = TinyCLI()

@cli.command
def test():
    """Print 'Test'"""
    print("Test") 

@cli.command
def say_hello(name: str = "John"):
    """Say hello"""
    print(f"Hello {name}")

if __name__ == "__main__":
    cli.run()

```

Example of execution

```bash

Welcome to TinyCLI
> ?
Commands:

	test	Print 'test'
	hello	Say Hello to name
> ? test
test 
> ? hello
hello NAME

Parameters:

		NAME	Type STRING, Required: False Default: John

>
```

