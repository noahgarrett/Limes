from enum import Enum
from typing import NamedTuple


SymbolScope = str

class ScopeType(Enum):
    GLOBAL_SCOPE: SymbolScope = "GLOBAL"
    LOCAL_SCOPE: SymbolScope = "LOCAL"
    BUILTIN_SCOPE: SymbolScope = "BUILTIN"
    FREE_SCOPE: SymbolScope = "FREE"
    FUNCTION_SCOPE: SymbolScope = "FUNCTION"


class Symbol(NamedTuple):
    name: str
    scope: SymbolScope
    index: int


class SymbolTable:
    def __init__(self, outer = None) -> None:
        self.outer: SymbolTable = outer

        self.store: dict[str, Symbol] = {}
        self.num_definitions: int = 0

        self.free_symbols: list[Symbol] = []

    def define(self, name: str) -> Symbol:
        symbol: Symbol = None

        if self.outer is None:
            symbol = Symbol(name=name, index=self.num_definitions, scope=ScopeType.GLOBAL_SCOPE)
        else:
            symbol = Symbol(name=name, index=self.num_definitions, scope=ScopeType.LOCAL_SCOPE)

        self.store[name] = symbol
        self.num_definitions += 1
        return symbol
    
    def define_builtin(self, index: int, name: str) -> Symbol:
        symbol: Symbol = Symbol(name=name, index=index, scope=ScopeType.BUILTIN_SCOPE)
        self.store[name] = symbol
        return symbol
    
    def define_free(self, original: Symbol) -> Symbol:
        self.free_symbols.append(original)

        symbol: Symbol = Symbol(name=original.name, index=len(self.free_symbols) - 1, scope=ScopeType.FREE_SCOPE)

        self.store[original.name] = symbol
        return symbol
    
    def define_function_name(self, name: str) -> Symbol:
        symbol = Symbol(name=name, index=0, scope=ScopeType.FUNCTION_SCOPE)
        self.store[name] = symbol
        return symbol
    
    def resolve(self, name: str) -> tuple[Symbol, bool]:
        obj: Symbol | None = self.store.get(name)
        if obj is None and self.outer is not None:
            obj, ok = self.outer.resolve(name)
            if not ok:
                return obj, ok
            
            if obj.scope == ScopeType.GLOBAL_SCOPE or obj.count == ScopeType.BUILTIN_SCOPE:
                return obj, ok
            
            free = self.define_free(obj)
            return free, True

        return obj, True if obj is not None else False
