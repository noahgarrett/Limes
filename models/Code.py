from enum import Enum, auto
from typing import NamedTuple, Dict
import struct


class OpCode(Enum):
    OpConstant = 0
    OpAdd = auto()
    OpSub = auto()
    OpMul = auto()
    OpDiv = auto()
    OpPop = auto()
    OpTrue = auto()
    OpFalse = auto()
    OpEqual = auto()
    OpNotEqual = auto()
    OpGreaterThan = auto()
    OpGreaterThanEqual = auto()
    OpMinus = auto()
    OpBang = auto()
    OpJumpNotTruthy = auto()
    OpJump = auto()
    OpNull = auto()
    OpGetGlobal = auto()
    OpSetGlobal = auto()
    OpArray = auto()
    OpHash = auto()
    OpIndex = auto()
    OpCall = auto()
    OpReturnValue = auto()
    OpReturn = auto()
    OpGetLocal = auto()
    OpSetLocal = auto()
    OpGetBuiltin = auto()
    OpClosure = auto()
    OpGetFree = auto()
    OpCurrentClosure = auto()
    OpImport = auto()


class Definition(NamedTuple):
    name: str
    operand_widths: list[int]

definitions: Dict[OpCode, Definition] = {
    OpCode.OpConstant: Definition("OpConstant", [2]),
    OpCode.OpAdd: Definition("OpAdd", []),
    OpCode.OpSub: Definition("OpSub", []),
    OpCode.OpMul: Definition("OpMul", []),
    OpCode.OpDiv: Definition("OpDiv", []),
    OpCode.OpPop: Definition("OpPop", []),
    OpCode.OpTrue: Definition("OpTrue", []),
    OpCode.OpFalse: Definition("OpFalse", []),
    OpCode.OpEqual: Definition("OpEqual", []),
    OpCode.OpNotEqual: Definition("OpNotEqual", []),
    OpCode.OpGreaterThan: Definition("OpGreaterThan", []),
    OpCode.OpGreaterThanEqual: Definition("OpGreaterThanEqual", []),
    OpCode.OpMinus: Definition("OpMinus", []),
    OpCode.OpBang: Definition("OpBang", []),
    OpCode.OpJumpNotTruthy: Definition("OpJumpNotTruthy", [2]),
    OpCode.OpJump: Definition("OpJump", [2]),
    OpCode.OpNull: Definition("OpNull", []),
    OpCode.OpGetGlobal: Definition("OpGetGlobal", [2]),
    OpCode.OpSetGlobal: Definition("OpSetGlobal", [2]),
    OpCode.OpArray: Definition("OpArray", [2]),
    OpCode.OpHash: Definition("OpHash", [2]),
    OpCode.OpIndex: Definition("OpIndex", []),
    OpCode.OpCall: Definition("OpCall", [1]),
    OpCode.OpReturnValue: Definition("OpReturnValue", []),
    OpCode.OpReturn: Definition("OpReturn", []),
    OpCode.OpGetLocal: Definition("OpGetLocal", [1]),
    OpCode.OpSetLocal: Definition("OpSetLocal", [1]),
    OpCode.OpGetBuiltin: Definition("OpGetBuiltin", [1]),
    OpCode.OpClosure: Definition("OpClosure", [2, 1]),
    OpCode.OpGetFree: Definition("OpGetFree", [1]),
    OpCode.OpCurrentClosure: Definition("OpCurrentClosure", []),
    OpCode.OpImport: Definition("OpImport", [2])
}

def lookup(op: int) -> tuple[Definition, str]:
    defin = definitions.get(op)
    if defin is None:
        return None, f"Opcode {op} is undefined."
    return defin, None


Instructions = bytearray

def make(op: OpCode, *operands: int) -> bytearray:
    defin: Definition = definitions.get(op)
    if defin is None:
        return b''
    
    instruction_len: int = 1 + sum(defin.operand_widths)    
    instruction: bytearray = bytearray(instruction_len)
    instruction[0] = op.value
    
    offset: int = 1
    for i, o in enumerate(operands):
        width: int = defin.operand_widths[i]
        match width:
            case 2:
                struct.pack_into(">H", instruction, offset, o)
            case 1:
                instruction[offset] = o
        
        offset += width
    
    return instruction

def as_string(ins: Instructions) -> str:
    output: str = ""

    i = 0
    while i < len(ins):
        defin, err = lookup(OpCode(ins[i]))
        if err is not None:
            output += "ERROR: {err}\n"
            continue

        operands, read = read_operands(defin, ins[i + 1:])
        output += f"{i:04d} {fmt_instruction(defin, operands)}\n"
        i = i + 1 + read

    return output

def fmt_instruction(defin: Definition, operands: list[int]) -> str:
    operand_count: int = len(defin.operand_widths)
    if len(operands) != operand_count:
        return f"ERROR: Operand length {len(operands)} does not match the defined {operand_count}"
    
    match operand_count:
        case 0:
            return defin.name
        case 1:
            return f"{defin.name} {operands[0]}"
        case 2:
            return f"{defin.name} {operands[0]} {operands[1]}"
        case _:
            return f"ERROR: Unhandled operand_count ({operand_count}) for {defin.name}"

def read_operands(defin: Definition, ins: Instructions) -> tuple[list[int], int]:
    operands: list[int] = []
    offset: int = 0

    for i, width in enumerate(defin.operand_widths):
        match width:
            case 2:
                operands.append(read_uint16(ins[offset:]))
            case 1:
                operands.append(read_uint8(ins[offset:]))
        offset += width
    
    return operands, offset

def read_uint16(ins: Instructions) -> int:
    return struct.unpack(">H", ins[:2])[0]

def read_uint8(ins) -> int:
    return ins[0]