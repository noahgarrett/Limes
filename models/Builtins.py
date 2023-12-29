from models.Object import Builtin, Object, ErrorObject, IntegerObject, NullObject
from typing import NamedTuple

NULL_OBJ = NullObject()

# region Builtins
def len_func(*args: Object) -> Object:
    if not len(args) == 1:
        return new_error(f"wrong number of arguments. got={len(args)}, want=1")
    
    match args[0].type():
        case "ARRAY":
            return IntegerObject(value=len(args[0].elements))
        case "STRING":
            return IntegerObject(value=len(args[0].value))
        case _:
            return new_error(f"argument to `len` not supported, got {args[0].type()}")
        
def print_func(*args: Object) -> Object:
    if not len(args) == 1:
        return new_error(f"wrong number of arguments for `print`. got={len(args)}, want=1")

    match args[0].type():
        case "INTEGER":
            print(args[0].value)
        case "BOOL":
            print(args[0].value)
        case "FLOAT":
            print(args[0].value)
        case "STRING":
            print(args[0].value)
        case _:
            return new_error(f"Object type {args[0].type()} not implemented for `print`")
        
    return NULL_OBJ
# endregion

# region Helpers
def new_error(format_msg: str, *a) -> ErrorObject:
    return ErrorObject(message=f"{format_msg} | {a}")
# endregion

class BuiltinItem(NamedTuple):
    name: str
    builtin: Builtin

Builtin_Functions: list[BuiltinItem] = [
    BuiltinItem(
        "len",
        Builtin(fn=len_func)
    ),
    BuiltinItem(
        "print",
        Builtin(fn=print_func)
    )
]

def get_builtin_by_name(name: str) -> Builtin:
    for defin in Builtin_Functions:
        if defin.name == name:
            return defin.builtin
    return None
