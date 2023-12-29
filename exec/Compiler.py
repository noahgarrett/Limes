from models.Code import Instructions, OpCode, make
from models.Object import Object, IntegerObject, StringObject, CompiledFunction, FloatObject
from models.Builtins import Builtin_Functions
from models.AST import Node, Program, ExpressionStatement, InfixExpression, IntegerLiteral, BooleanLiteral, PrefixExpression, IfExpression
from models.AST import BlockStatement, LetStatement, IdentifierLiteral, StringLiteral, ArrayLiteral, HashLiteral, Expression, IndexExpression
from models.AST import FunctionLiteral, ReturnStatement, CallExpression, ImportStatement, WhileStatement, AssignStatement, ForStatement, FloatLiteral
from models.SymbolTable import SymbolTable, Symbol, ScopeType

from exec.Lexer import Lexer
from exec.Parser import Parser

from dataclasses import dataclass

@dataclass
class Bytecode:
    instructions: Instructions
    constants: list[Object]

@dataclass
class EmittedInstruction:
    opcode: OpCode = None
    position: int = None

@dataclass
class CompilationScope:
    instructions: Instructions
    last_instruction: EmittedInstruction
    previous_instruction: EmittedInstruction


class Compiler:
    def __init__(self, symbol_table: SymbolTable = None, constants: list[Object] = None, debug: bool = False) -> None:
        self.debug: bool = debug

        self.instructions: Instructions = Instructions()
        self.constants: list[Object] = [] if constants is None else constants

        self.symbol_table: SymbolTable = SymbolTable() if symbol_table is None else symbol_table

        # Handle Builtins
        for i, v in enumerate(Builtin_Functions):
            self.symbol_table.define_builtin(i, v.name)

        # Handle Scope
        main_scope: CompilationScope = CompilationScope(
            instructions=Instructions(),
            last_instruction=EmittedInstruction(),
            previous_instruction=EmittedInstruction()
        )

        self.scopes: list[CompilationScope] = [main_scope]
        self.scope_index: int = 0

    def bytecode(self) -> Bytecode:
        return Bytecode(instructions=self.current_instructions(), constants=self.constants)

    def compile(self, node: Node) -> str:
        match node.type():
            # Statements
            case "Program":
                node: Program = node
                for stmt in node.statements:
                    err = self.compile(stmt)
                    if err is not None:
                        return err
            case "ExpressionStatement":
                node: ExpressionStatement = node
                err = self.compile(node.expr)
                if err is not None:
                    return err
                
                self.emit(OpCode.OpPop)
            case "BlockStatement":
                node: BlockStatement = node
                for stmt in node.statements:
                    err = self.compile(stmt)
                    if err is not None:
                        return err
            case "LetStatement":
                node: LetStatement = node

                symbol: Symbol = self.symbol_table.define(node.name.value)

                err = self.compile(node.value)
                if err is not None:
                    return err
                
                if symbol.scope == ScopeType.GLOBAL_SCOPE:
                    self.emit(OpCode.OpSetGlobal, symbol.index)
                else:
                    self.emit(OpCode.OpSetLocal, symbol.index)
            case "ReturnStatement":
                node: ReturnStatement = node
                err = self.compile(node.return_value)
                if err is not None:
                    return err
                
                self.emit(OpCode.OpReturnValue)
            case "ImportStatement":
                node: ImportStatement = node

                with open(f"debug/{node.file_path}", "r") as f:
                    src: str = f.read()

                l: Lexer = Lexer(source=src)
                p: Parser = Parser(lexer=l)

                err = self.compile(p.parse_program())
                if err is not None:
                    return err
            case "WhileStatement":
                node: WhileStatement = node

                start_loop_pos: int = len(self.current_instructions())

                err = self.compile(node.condition)
                if err is not None:
                    return err

                jump_not_truthy_pos: int = self.emit(OpCode.OpJumpNotTruthy, 6969)

                err = self.compile(node.body)
                if err is not None:
                    return err
                
                offset = len(self.current_instructions()) - start_loop_pos + 1
                self.emit(OpCode.OpLoop, offset)

                after_body_pos: int = len(self.current_instructions())
                self.change_operand(jump_not_truthy_pos, after_body_pos)
            case "ForStatement":
                node: ForStatement = node

                err = self.compile(node.initializer)
                if err is not None:
                    return err
                
                start_condition_pos: int = len(self.current_instructions())

                err = self.compile(node.condition)
                if err is not None:
                    return err
                
                jump_not_truthy_pos: int = self.emit(OpCode.OpJumpNotTruthy, 6969)

                err = self.compile(node.increment)
                if err is not None:
                    return err
                
                err = self.compile(node.body)
                if err is not None:
                    return err
                
                offset = len(self.current_instructions()) - start_condition_pos + 1
                self.emit(OpCode.OpLoop, offset)

                after_body_pos: int = len(self.current_instructions())
                self.change_operand(jump_not_truthy_pos, after_body_pos)
            case "AssignStatement":
                node: AssignStatement = node

                existing_symbol, ok = self.symbol_table.resolve(node.ident.value)
                if not ok:
                    return f"Undefined variable: `{node.ident.value}`"

                err = self.compile(node.right_value)
                if err is not None:
                    return err
                
                if existing_symbol.scope == ScopeType.GLOBAL_SCOPE:
                    self.emit(OpCode.OpSetGlobal, existing_symbol.index)
                else:
                    self.emit(OpCode.OpSetLocal, existing_symbol.index)
                
            # Expressions
            case "InfixExpression":
                node: InfixExpression = node

                if node.operator == "<":
                    err = self.compile(node.right_node)
                    if err is not None:
                        return err
                    
                    err = self.compile(node.left_node)
                    if err is not None:
                        return err
                    
                    self.emit(OpCode.OpGreaterThan)
                    return None
            
                err = self.compile(node.left_node)
                if err is not None:
                    return err
                
                err = self.compile(node.right_node)
                if err is not None:
                    return err
                
                match node.operator:
                    case "+":
                        self.emit(OpCode.OpAdd)
                    case "-":
                        self.emit(OpCode.OpSub)
                    case "*":
                        self.emit(OpCode.OpMul)
                    case "/":
                        self.emit(OpCode.OpDiv)
                    case ">":
                        self.emit(OpCode.OpGreaterThan)
                    case "==":
                        self.emit(OpCode.OpEqual)
                    case "!=":
                        self.emit(OpCode.OpNotEqual)
                    case _:
                        return f"Unknown Infix Operator: {node.operator}"
            case "PrefixExpression":
                node: PrefixExpression = node

                err = self.compile(node.right_node)
                if err is not None:
                    return err
                
                match node.operator:
                    case "!":
                        self.emit(OpCode.OpBang)
                    case "-":
                        self.emit(OpCode.OpMinus)
                    case _:
                        return f"Unknown Prefix Operator: {node.operator}"
            case "IfExpression":
                node: IfExpression = node
                err = self.compile(node.condition)
                if err is not None:
                    return err
                
                jump_not_truthy_pos: int = self.emit(OpCode.OpJumpNotTruthy, 6969)

                err = self.compile(node.consequence)
                if err is not None:
                    return err
                
                if self.last_instruction_is(OpCode.OpPop):
                    self.remove_last_pop()

                jump_pos: int = self.emit(OpCode.OpJump, 420)

                after_consequence_pos: int = len(self.current_instructions())
                self.change_operand(jump_not_truthy_pos, after_consequence_pos)

                if node.alternative is None:
                    self.emit(OpCode.OpNull)
                else:
                    err = self.compile(node.alternative)
                    if err is not None:
                        return err
                    
                    if self.last_instruction_is(OpCode.OpPop):
                        self.remove_last_pop()
                    
                after_alternative_pos: int = len(self.current_instructions())
                self.change_operand(jump_pos, after_alternative_pos)
            case "IndexExpression":
                node: IndexExpression = node
                err = self.compile(node.left)
                if err is not None:
                    return err
                
                err = self.compile(node.index)
                if err is not None:
                    return err
                
                self.emit(OpCode.OpIndex)
            case "CallExpression":
                node: CallExpression = node
                err = self.compile(node.function)
                if err is not None:
                    return err
                
                for arg in node.arguments:
                    err = self.compile(arg)
                    if err is not None:
                        return err
                
                self.emit(OpCode.OpCall, len(node.arguments))
                
            # Literals
            case "IntegerLiteral":
                node: IntegerLiteral = node

                integer: IntegerObject = IntegerObject(value=node.value)
                self.emit(OpCode.OpConstant, self.add_constant(integer))
            case "FloatLiteral":
                node: FloatLiteral = node

                f_loat: FloatObject = FloatObject(value=node.value)
                self.emit(OpCode.OpConstant, self.add_constant(f_loat))
            case "BooleanLiteral":
                node: BooleanLiteral = node

                if node.value:
                    self.emit(OpCode.OpTrue)
                else:
                    self.emit(OpCode.OpFalse)
            case "IdentifierLiteral":
                node: IdentifierLiteral = node
                symbol, ok = self.symbol_table.resolve(node.value)
                if not ok:
                    return f"Undefined variable {node.value}"
                
                self.load_symbol(symbol)
            case "StringLiteral":
                node: StringLiteral = node

                string: StringObject = StringObject(value=node.value)
                self.emit(OpCode.OpConstant, self.add_constant(string))
            case "ArrayLiteral":
                node: ArrayLiteral = node
                for element in node.elements:
                    err = self.compile(element)
                    if err is not None:
                        return err
                
                self.emit(OpCode.OpArray, len(node.elements))
            case "HashLiteral":
                node: HashLiteral = node

                keys: list[Expression] = []
                for k in node.pairs:
                    keys.append(k)
                
                keys.sort(key=lambda key: key.string())

                for ky in keys:
                    err = self.compile(ky)
                    if err is not None:
                        return err
                    
                    err = self.compile(node.pairs[ky])
                    if err is not None:
                        return err
                    
                self.emit(OpCode.OpHash, len(node.pairs) * 2)
            case "FunctionLiteral":
                node: FunctionLiteral = node

                self.enter_scope()

                if not node.name == "":
                    self.symbol_table.define_function_name(node.name)

                for param in node.parameters:
                    self.symbol_table.define(param.value)

                err = self.compile(node.body)
                if err is not None:
                    return err
                
                if self.last_instruction_is(OpCode.OpPop):
                    self.replace_last_pop_with_return()

                if not self.last_instruction_is(OpCode.OpReturnValue):
                    self.emit(OpCode.OpReturn)
                
                free_symbols = self.symbol_table.free_symbols
                num_locals: int = self.symbol_table.num_definitions
                ins = self.leave_scope()

                for sym in free_symbols:
                    self.load_symbol(sym)

                compiled_fn: CompiledFunction = CompiledFunction(instructions=ins, num_locals=num_locals, num_params=len(node.parameters))
                fn_index: int = self.add_constant(compiled_fn)
                
                self.emit(OpCode.OpClosure, fn_index, len(free_symbols))

    # region Compiler Helpers
    def emit(self, op: OpCode, *operands: int) -> int:
        ins: Instructions = make(op, *operands)
        pos: int = self.add_instruction(ins)

        self.set_last_instruction(op, pos)

        return pos
    
    def set_last_instruction(self, op: OpCode, pos: int):
        previous = self.scopes[self.scope_index].last_instruction
        last = EmittedInstruction(opcode=op, position=pos)

        self.scopes[self.scope_index].previous_instruction = previous
        self.scopes[self.scope_index].last_instruction = last
    
    def add_instruction(self, ins: Instructions) -> int:
        pos_new_ins: int = len(self.current_instructions())
        updated_ins = self.current_instructions() + ins

        self.scopes[self.scope_index].instructions = updated_ins
        return pos_new_ins

    def add_constant(self, obj: Object) -> int:
        self.constants.append(obj)
        return len(self.constants) - 1
    
    def last_instruction_is(self, op: OpCode) -> bool:
        if len(self.current_instructions()) == 0:
            return False
        
        return self.scopes[self.scope_index].last_instruction.opcode == op
    
    def replace_last_pop_with_return(self):
        last_pos = self.scopes[self.scope_index].last_instruction.position
        self.replace_instruction(last_pos, make(OpCode.OpReturnValue))

        self.scopes[self.scope_index].last_instruction.opcode = OpCode.OpReturnValue

    def remove_last_pop(self):
        last = self.scopes[self.scope_index].last_instruction
        previous = self.scopes[self.scope_index].previous_instruction

        old = self.current_instructions()
        new = old[:last.position]

        self.scopes[self.scope_index].instructions = new
        self.scopes[self.scope_index].last_instruction = previous

    def replace_instruction(self, pos: int, new_instruction: Instructions):
        for i in range(0, len(new_instruction), 1):
            self.scopes[self.scope_index].instructions[pos + i] = new_instruction[i]
    
    def change_operand(self, op_pos: int, operand: int):
        op: OpCode = OpCode(self.current_instructions()[op_pos])
        new_instruction: Instructions = make(op, operand)

        self.replace_instruction(op_pos, new_instruction)

    def current_instructions(self) -> Instructions:
        return self.scopes[self.scope_index].instructions
    
    def enter_scope(self):
        scope: CompilationScope = CompilationScope(
            instructions=Instructions(),
            last_instruction=EmittedInstruction(),
            previous_instruction=EmittedInstruction()
        )

        self.symbol_table = SymbolTable(outer=self.symbol_table)

        self.scopes.append(scope)
        self.scope_index += 1

    def leave_scope(self):
        ins = self.current_instructions()

        self.symbol_table = self.symbol_table.outer

        self.scopes = self.scopes[:len(self.scopes) - 1]
        self.scope_index -= 1

        return ins
    
    def load_symbol(self, s: Symbol):
        if s.scope == ScopeType.GLOBAL_SCOPE:
            self.emit(OpCode.OpGetGlobal, s.index)
        elif s.scope == ScopeType.LOCAL_SCOPE:
            self.emit(OpCode.OpGetLocal, s.index)
        elif s.scope == ScopeType.BUILTIN_SCOPE:
            self.emit(OpCode.OpGetBuiltin, s.index)
        elif s.scope == ScopeType.FREE_SCOPE:
            self.emit(OpCode.OpGetFree, s.index)
        elif s.scope == ScopeType.FUNCTION_SCOPE:
            self.emit(OpCode.OpCurrentClosure)
    # endregion