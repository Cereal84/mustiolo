from dataclasses import dataclass

@dataclass
class FunctionLocation:
    filename: str
    lineno: int

@dataclass
class FunctionMetadata:
    """
    This class contains some of the function information we need to
    describe and validate the function or locate it for error messages.
    Probably store this kind of informations can be avoided and then retrieves
    them only if necessary.
    """
    name: str
    argscount: int
    docstring: str
    location: FunctionLocation
