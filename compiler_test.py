from typing import NamedTuple
from models.Object import Object, CompiledFunction
from models.Code import Instructions, make, OpCode, as_string
from models.AST import Program
from exec.Lexer import Lexer
from exec.Parser import Parser
from exec.Compiler import Compiler

class CompilerTestCase(NamedTuple):
    input_src: str
    expected_constants: list
    expected_instructions: list[Instructions]


def test_builder():
    tests: list[CompilerTestCase] = [
        CompilerTestCase("1 + 2", [1, 2], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpConstant, 1),
            make(OpCode.OpAdd),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("1 - 2", [1, 2], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpConstant, 1),
            make(OpCode.OpSub),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("1 * 2", [1, 2], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpConstant, 1),
            make(OpCode.OpMul),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("1 / 2", [1, 2], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpConstant, 1),
            make(OpCode.OpDiv),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("1; 2", [1, 2], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpPop),
            make(OpCode.OpConstant, 1),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("-1", [1], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpMinus),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("!true;", [], [
            make(OpCode.OpTrue),
            make(OpCode.OpBang),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("if true { 10; }; 3333;", [10, 3333], [
            make(OpCode.OpTrue),
            make(OpCode.OpJumpNotTruthy, 10),
            make(OpCode.OpConstant, 0),
            make(OpCode.OpJump, 11),
            make(OpCode.OpNull),
            make(OpCode.OpPop),
            make(OpCode.OpConstant, 1),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("if true { 10; } else { 20; }; 3333;", [10, 20, 3333], [
            make(OpCode.OpTrue),
            make(OpCode.OpJumpNotTruthy, 10),
            make(OpCode.OpConstant, 0),
            make(OpCode.OpJump, 13),
            make(OpCode.OpConstant, 1),
            make(OpCode.OpPop),
            make(OpCode.OpConstant, 2),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("let one = 1; let two = 2;", [1, 2], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpSetGlobal, 0),
            make(OpCode.OpConstant, 1),
            make(OpCode.OpSetGlobal, 1)
        ]),
        CompilerTestCase("let one = 1; one;", [1], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpSetGlobal, 0),
            make(OpCode.OpGetGlobal, 0),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("[]", [], [
            make(OpCode.OpArray, 0),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("[1, 2, 3]", [1, 2, 3], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpConstant, 1),
            make(OpCode.OpConstant, 2),
            make(OpCode.OpArray, 3),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("{}", [], [
            make(OpCode.OpHash, 0),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("{1: 2, 3: 4, 5: 6}", [1, 2, 3, 4, 5, 6], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpConstant, 1),
            make(OpCode.OpConstant, 2),
            make(OpCode.OpConstant, 3),
            make(OpCode.OpConstant, 4),
            make(OpCode.OpConstant, 5),
            make(OpCode.OpHash, 6),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("[1, 2, 3][1 + 1];", [1, 2, 3, 1, 1], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpConstant, 1),
            make(OpCode.OpConstant, 2),
            make(OpCode.OpArray, 3),
            make(OpCode.OpConstant, 3),
            make(OpCode.OpConstant, 4),
            make(OpCode.OpAdd),
            make(OpCode.OpIndex),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("{1: 2}[2 - 1];", [1, 2, 2, 1], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpConstant, 1),
            make(OpCode.OpHash, 2),
            make(OpCode.OpConstant, 2),
            make(OpCode.OpConstant, 3),
            make(OpCode.OpSub),
            make(OpCode.OpIndex),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("fn() { return 5 + 10; }", [
            5, 10, [
                make(OpCode.OpConstant, 0),
                make(OpCode.OpConstant, 1),
                make(OpCode.OpAdd),
                make(OpCode.OpReturnValue)
            ]
        ], [
            make(OpCode.OpConstant, 2),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("fn() { 5 + 10; };", [
            5, 10, [
                make(OpCode.OpConstant, 0),
                make(OpCode.OpConstant, 1),
                make(OpCode.OpAdd),
                make(OpCode.OpReturnValue)
            ]
        ], [
            make(OpCode.OpConstant, 2),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("fn() { 1; 2 }", [
            1, 2, [
                make(OpCode.OpConstant, 0),
                make(OpCode.OpPop),
                make(OpCode.OpConstant, 1),
                make(OpCode.OpReturnValue)
            ]
        ], [
            make(OpCode.OpConstant, 2),
            make(OpCode.OpPop)
        ]),
        CompilerTestCase("fn() { }", [
            [
                make(OpCode.OpReturn)
            ]
        ], [
            make(OpCode.OpConstant, 0),
            make(OpCode.OpPop)
        ])
    ]

    return tests


def parse(input_src: str) -> Program:
    l = Lexer(input_src)
    p = Parser(l)
    return p.parse_program()

def test_instructions(expected: list[Instructions], actual: Instructions):
    concatted = concat_instructions(expected)

    if len(actual) != len(concatted):
        return f"Wrong Instructions Length.\nwant=\n{as_string(concatted)}\ngot=\n{as_string(actual)}"
    
    for i, ins in enumerate(concatted):
        if actual[i] != ins:
            return f"Wrong Instruction At {i}.\nwant=\n{as_string(concatted)}\ngot=\n{as_string(actual)}"
    
    return None

def test_constants(expected: list, actual: list[Object]) -> str:
    if len(expected) != len(actual):
        return f"Wrong number of constants. got={len(actual)}, want={len(expected)}"
    
    for i, constant in enumerate(expected):
        if isinstance(constant, int):
            err = test_integer_object(int(constant), actual[i])
            if err is not None:
                return f"constant {i} - testIntegerObject failed: {err}"
        elif isinstance(constant, list):
            if not isinstance(actual[i], CompiledFunction):
                return f"constant {i} - not a function: {actual[i]}"
            
def test_integer_object(expected: int, actual: Object) -> str:
    if not actual.type() == "INTEGER":
        return f"Object is not Integer. got={actual.__name__} ({actual})"
    
    if actual.value != expected:
        return f"Object has wrong value. got={actual.value}, want={expected}"

def concat_instructions(s: list[Instructions]) -> Instructions:
    out = Instructions()

    for ins in s:
        out += ins
    
    return out

def run():
    tests: list[CompilerTestCase] = [t for t in test_builder()]

    for t in tests:
        program = parse(t.input_src)

        compiler = Compiler()
        err = compiler.compile(program)
        if err is not None:
            print(f"Compiler error: {err}")
            exit(1)
        
        bytecode = compiler.bytecode()

        err = test_instructions(t.expected_instructions, bytecode.instructions)
        if err is not None:
            print(f"testInstructions failed: {err}")
            exit(1)
        
        err = test_constants(t.expected_constants, bytecode.constants)
        if err is not None:
            print(f"testConstants failed: {err}")
            exit(1)

if __name__ == '__main__':
    run()