from typing import List, Callable
from mustiolo.cli import ParameterModel


def get_defaults(fn: Callable):
    """
    Get the default values of the passed function or method.
        """
    output = {}
    if fn.__defaults__ is not None:
        # Get the names of all provided default values for args
        default_varnames = list(fn.__code__.co_varnames)[:fn.__code__.co_argcount][-len(fn.__defaults__):]
        # Update the output dictionary with the default values
        output.update(dict(zip(default_varnames, fn.__defaults__)))
    if fn.__kwdefaults__ is not None:
        # Update the output dictionary with the keyword default values
        output.update(fn.__kwdefaults__)
    return output

def parse_parameters(f: Callable) -> List[ParameterModel]:
    parameters = []
    defaults = get_defaults(f)
    for pname, ptype in f.__annotations__.items():
        parameters.append(ParameterModel(name=pname, ptype=ptype, default=(defaults.get(pname, None))))

    return parameters