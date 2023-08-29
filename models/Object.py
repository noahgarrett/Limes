from abc import ABC, abstractmethod
from models.Code import Instructions
from typing import NamedTuple, Callable
import hashlib

# Object Types
T_INTEGER_OBJ = "INTEGER"
T_FLOAT_OBJ = "FLOAT"
T_BOOL_OBJ = "BOOL"
T_NULL_OBJ = "NULL"
T_ERROR_OBJ = "ERROR"
T_COMPILED_FUNCTION_OBJ = "COMPILED_FUNCTION_OBJ"
T_CLOSURE_OBJ = "CLOSURE"
T_STRING_OBJ = "STRING"
T_ARRAY_OBJ = "ARRAY"
T_HASH_OBJ = "HASH"
T_BUILTIN_OBJ = "BUILTIN"

class Object(ABC):
    @abstractmethod
    def type(self) -> str:
        pass

    @abstractmethod
    def inspect(self) -> str:
        pass

class HashPair(NamedTuple):
    key: Object
    value: Object

class HashKey(NamedTuple):
    type: str
    value: int

class Hashable(ABC):
    @abstractmethod
    def hash_key(self) -> HashKey:
        pass

class IntegerObject(Object, Hashable):
    def __init__(self, value: int) -> None:
        self.value: int = value

    def type(self) -> str:
        return T_INTEGER_OBJ
    
    def inspect(self) -> str:
        return str(self.value)
    
    def hash_key(self) -> HashKey:
        return HashKey(type=self.type(), value=int(self.value))
    
class FloatObject(Object):
    def __init__(self, value: float) -> None:
        self.value: float = value

    def type(self) -> str:
        return T_FLOAT_OBJ
    
    def inspect(self) -> str:
        return str(self.value)

    
class StringObject(Object, Hashable):
    def __init__(self, value: str) -> None:
        self.value: str = value

    def type(self) -> str:
        return T_STRING_OBJ
    
    def inspect(self) -> str:
        return str(self.value)
    
    def hash_key(self) -> HashKey:
        h = hashlib.sha256()
        h.update(self.value.encode("utf-8"))
        return HashKey(type=self.type(), value=h.digest()[::-1].hex())
    
class BooleanObject(Object, Hashable):
    def __init__(self, value: bool) -> None:
        self.value = value

    def type(self) -> str:
        return T_BOOL_OBJ
    
    def inspect(self) -> str:
        return str(self.value)
    
    def hash_key(self) -> HashKey:
        value: int = 0

        if self.value:
            value = 1
        
        return HashKey(type=self.type(), value=value)
    

class ArrayObject(Object):
    def __init__(self, elements: list[Object] = None) -> None:
        self.elements: list[Object] = [] if elements is None else elements
    
    def type(self) -> str:
        return T_ARRAY_OBJ
    
    def inspect(self) -> str:
        output: str = ""

        elements: list[str] = [el.inspect() for el in self.elements]

        output += "["
        output += ", ".join(elements)
        output += "]"
        return output
    

class HashObject(Object):
    def __init__(self, pairs: dict[HashKey, HashPair] = None) -> None:
        self.pairs = {} if pairs is None else pairs
    
    def type(self) -> str:
        return T_HASH_OBJ
    
    def inspect(self) -> str:
        output: str = ""

        pairs: list[str] = []
        for _, pair in self.pairs.items():
            pairs.append(f"{pair.key.inspect()}: {pair.value.inspect()}")

        output += "{"
        output += ", ".join(pairs)
        output += "}"
        return output
        
    
class NullObject(Object):
    def type(self) -> str:
        return T_NULL_OBJ
    
    def inspect(self) -> str:
        return "null"
    
class ErrorObject(Object):
    def __init__(self, message: str) -> None:
        self.message: str = message

    def type(self) -> str:
        return T_ERROR_OBJ
    
    def inspect(self) -> str:
        return f"ERROR: {self.message}"
    
class CompiledFunction(Object):
    def __init__(self, instructions: Instructions = None, num_locals: int = None, num_params: int = None) -> None:
        self.instructions: Instructions = instructions
        self.num_locals: int = 0 if num_locals is None else num_locals
        self.num_parameters: int = 0 if num_params is None else num_params

    def type(self) -> str:
        return T_COMPILED_FUNCTION_OBJ
    
    def inspect(self) -> str:
        return f"CompiledFunction[{self}]"
    
class ClosureObject(Object):
    def __init__(self, fn: CompiledFunction = None, free: list[Object] = None) -> None:
        self.fn = fn
        self.free = free
    
    def type(self) -> str:
        return T_CLOSURE_OBJ
    
    def inspect(self) -> str:
        return f"Closure[{self}]"


BuiltinFunction = Callable

class Builtin(Object):
    def __init__(self, fn: BuiltinFunction) -> None:
        self.fn = fn
    
    def type(self) -> str:
        return T_BUILTIN_OBJ
    
    def inspect(self) -> str:
        return "builtin function"