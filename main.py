from exec.Lexer import Lexer
from exec.Parser import Parser
from exec.Compiler import Compiler
from exec.VM import VM
from time import time

DEBUG: bool = False

if __name__ == '__main__':
    with open("debug/test.lime", "r") as f:
        code: str = f.read()
    
    l: Lexer = Lexer(source=code)

    p: Parser = Parser(lexer=l)

    st = time()
    program = p.parse_program()
    if len(p.errors) > 0:
        for err in p.errors:
            print(err)
        exit(1)

    if DEBUG:
        for s in program.statements:
            print(s.string())
    
    comp: Compiler = Compiler()
    err = comp.compile(program)
    if err is not None:
        print(f"Compiler Error:\n {err}\n")
        exit(1)
    
    machine: VM = VM(comp.bytecode())
    err = machine.run()
    if err is not None:
        print(f"Runtime Error:\n {err}\n")
        exit(1)
    et = time()
    execution_time = et - st

    if DEBUG:
        print(f"\n== Ending Stack (SP:{machine.stack.sp}) ==\n{[i.inspect() if i is not None else i for i in machine.stack.items[0:10]]}")
    
    last_popped = machine.stack.last_popped_elem

    if DEBUG:
        print(f"\n== Last Popped ==\n{last_popped.inspect()}\n")

    print(f"\n== Program executed in: {round(execution_time * 1000, 2)} ms. ({round(execution_time, 2)} sec.) ==")
