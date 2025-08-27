import re
from typing import Any, Callable, Dict, List

from mustiolo.exception import ParameterMissingType
from mustiolo.models.function_info import FunctionLocation, FunctionMetadata
from mustiolo.models.parameters import ParameterModel


def get_defaults(fn: Callable) -> Dict[str, Any]:
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


def parse_docstring_for_menu_usage(fn: Callable) -> List[str]:
    """
    This function retrieve the short help message and long help message
    from the docstring in the function.

    From docstring we exprect 2 sections:
        - menu
        - usage

    The first one is the message used in the help menu.
    The second one is the message used in the usage message.

    These messages are limited between tags
    <menu></menu>
    <usage></usage>

    """
    def get_section(text: str , pattern: str) -> str:
        match = re.search(pattern, text, re.DOTALL)

        # Check if a match is found and extract the substring
        if match:
            # it can be multiline and have whitespaces to be stripped.
            lines = [line.strip() for line in match.group(1).split("\n")]
            return "\n".join(lines)
        return ""

    if fn.__doc__ is None:
        return ["",""]

    help_msg: List[str] = []

    menu_pattern = r"\<menu\>(.*?)\<\/menu\>"
    usage_pattern = r"\<usage\>(.*?)\<\/usage\>"

    help_msg.append(get_section(fn.__doc__, menu_pattern))
    help_msg.append(get_section(fn.__doc__, usage_pattern))

    return help_msg


def get_function_location(fn: Callable) -> FunctionLocation:
    return FunctionLocation(filename=fn.__code__.co_filename, lineno=fn.__code__.co_firstlineno)


def get_function_metadata(fn: Callable) -> FunctionMetadata:

    name = fn.__name__
    docstring = fn.__doc__
    argscount = fn.__code__.co_argcount
    location = get_function_location(fn)

    return FunctionMetadata(name=name, docstring=docstring, argscount=argscount, location=location)


def parse_parameters(f: Callable, metavars: dict[str, str]) -> List[ParameterModel]:
    parameters = []
    defaults = get_defaults(f)

    if len(f.__annotations__.keys()) != f.__code__.co_argcount:
        # so not all the parameters have an annotation
        fmeta = get_function_metadata(f)
        raise ParameterMissingType(fmeta.name, fmeta.location.filename, fmeta.location.lineno)

    for pname, ptype in f.__annotations__.items():
        parameters.append(ParameterModel(name=pname, ptype=ptype, default=(defaults.get(pname, None)), metavar=metavars.get(pname)))

    return parameters
