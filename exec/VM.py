from exec.Compiler import Bytecode
from models.Stack import VMStack, FrameStack
from models.Code import Instructions, OpCode, read_uint16, read_uint8
from models.Object import Object, IntegerObject, FloatObject, BooleanObject, NullObject, StringObject, ArrayObject, HashObject, ClosureObject
from models.Object import HashKey, HashPair, Hashable, CompiledFunction
from models.Object import T_INTEGER_OBJ, T_FLOAT_OBJ, T_STRING_OBJ, T_ARRAY_OBJ, T_HASH_OBJ
from models.Builtins import Builtin_Functions, Builtin
from models.Frame import Frame
from exec.Lexer import Lexer
from exec.Parser import Parser
from exec.Compiler import Compiler

TRUE_OBJ = BooleanObject(value=True)
FALSE_OBJ = BooleanObject(value=False)
NULL_OBJ = NullObject()

class VM:
    def __init__(self, bytecode: Bytecode, globs: list[Object] = None, debug: bool = False) -> None:
        self.debug: bool = debug

        self.constants: list[Object] = bytecode.constants

        self.stack: VMStack = VMStack()

        self.globals: list[Object] = [] if globs is None else globs

        main_fn: CompiledFunction = CompiledFunction(instructions=bytecode.instructions)
        main_closure: ClosureObject = ClosureObject(fn=main_fn)
        main_frame: Frame = Frame(cl=main_closure, base_pointer=0)

        self.frames: FrameStack = FrameStack()
        self.push_frame(main_frame)

    def run(self):
        ip: int = None
        ins: Instructions = None
        op: OpCode = None

        while self.current_frame().ip < len(self.current_frame().instructions()) - 1:
            self.current_frame().ip += 1

            ip = self.current_frame().ip
            ins = self.current_frame().instructions()
            op: OpCode = OpCode(ins[ip])

            if self.debug:
                print(f"Stack ({str(op).replace('OpCode.', '')}) -> {[i.inspect() if i is not None else i for i in self.stack.items[0:10]]}")
            
            match op:
                case OpCode.OpConstant:
                    const_index: int = read_uint16(ins[ip + 1:])
                    self.current_frame().ip += 2

                    err = self.push(self.constants[const_index])
                    if err is not None:
                        return err
                case OpCode.OpAdd:
                    err = self.execute_binary_operation(op)
                    if err is not None:
                        return err
                case OpCode.OpSub:
                    err = self.execute_binary_operation(op)
                    if err is not None:
                        return err
                case OpCode.OpMul:
                    err = self.execute_binary_operation(op)
                    if err is not None:
                        return err
                case OpCode.OpDiv:
                    err = self.execute_binary_operation(op)
                    if err is not None:
                        return err
                case OpCode.OpPop:
                    self.pop()
                case OpCode.OpTrue:
                    err = self.push(TRUE_OBJ)
                    if err is not None:
                        return err
                case OpCode.OpFalse:
                    err = self.push(FALSE_OBJ)
                    if err is not None:
                        return err
                case OpCode.OpEqual:
                    err = self.execute_comparison(op)
                    if err is not None:
                        return err
                case OpCode.OpNotEqual:
                    err = self.execute_comparison(op)
                    if err is not None:
                        return err
                case OpCode.OpGreaterThan:
                    err = self.execute_comparison(op)
                    if err is not None:
                        return err
                case OpCode.OpBang:
                    err = self.execute_bang_operator()
                    if err is not None:
                        return err
                case OpCode.OpMinus:
                    err = self.execute_minus_operator()
                    if err is not None:
                        return err
                case OpCode.OpJump:
                    pos: int = read_uint16(ins[ip + 1:])
                    self.current_frame().ip = pos - 1
                case OpCode.OpJumpNotTruthy:
                    pos: int = read_uint16(ins[ip + 1:])
                    self.current_frame().ip += 2

                    condition = self.pop()
                    if not self.is_truthy(condition):
                        self.current_frame().ip = pos - 1
                case OpCode.OpNull:
                    err = self.push(NULL_OBJ)
                    if err is not None:
                        return err
                case OpCode.OpSetGlobal:
                    global_index: int = read_uint16(ins[ip + 1:])
                    self.current_frame().ip += 2

                    self.globals.append(self.pop())
                case OpCode.OpGetGlobal:
                    global_index: int = read_uint16(ins[ip + 1:])
                    self.current_frame().ip += 2

                    err = self.push(self.globals[global_index])
                    if err is not None:
                        return err
                case OpCode.OpArray:
                    num_elements: int = read_uint16(ins[ip + 1:])
                    self.current_frame().ip += 2

                    array = self.build_array(self.stack.sp - num_elements, self.stack.sp)
                    self.stack.sp = self.stack.sp - num_elements

                    err = self.push(array)
                    if err is not None:
                        return err
                case OpCode.OpHash:
                    num_elements: int = read_uint16(ins[ip + 1:])
                    self.current_frame().ip += 2

                    h, err = self.build_hash(self.stack.sp - num_elements, self.stack.sp)
                    if err is not None:
                        return err
                    
                    self.stack.sp = self.stack.sp - num_elements

                    err = self.push(h)
                    if err is not None:
                        return err
                case OpCode.OpIndex:
                    index = self.pop()
                    left = self.pop()

                    err = self.execute_index_expression(left, index)
                    if err is not None:
                        return err
                case OpCode.OpCall:
                    num_args: int = read_uint8(ins[ip + 1:])
                    self.current_frame().ip += 1

                    err = self.execute_call(num_args)
                    if err is not None:
                        return err
                case OpCode.OpReturnValue:
                    return_value = self.pop()

                    frame = self.pop_frame()
                    # self.pop()
                    self.stack.sp = frame.base_pointer - 1

                    err = self.push(return_value)
                    if err is not None:
                        return err
                case OpCode.OpReturn:
                    frame = self.pop_frame()
                    # self.pop()
                    self.stack.sp = frame.base_pointer - 1

                    err = self.push(NULL_OBJ)
                    if err is not None:
                        return err
                case OpCode.OpSetLocal:
                    local_index: int = read_uint8(ins[ip + 1:])
                    self.current_frame().ip += 1

                    frame = self.current_frame()

                    self.stack.items[frame.base_pointer + local_index] = self.pop()
                case OpCode.OpGetLocal:
                    local_index: int = read_uint8(ins[ip + 1:])
                    self.current_frame().ip += 1

                    frame = self.current_frame()

                    err = self.push(self.stack.items[frame.base_pointer + local_index])
                    if err is not None:
                        return err
                case OpCode.OpGetBuiltin:
                    builtin_index: int = read_uint8(ins[ip + 1:])
                    self.current_frame().ip += 1

                    defin = Builtin_Functions[builtin_index]

                    err = self.push(defin.builtin)
                    if err is not None:
                        return err
                case OpCode.OpClosure:
                    const_index: int = read_uint16(ins[ip + 1:])
                    num_free: int = read_uint8(ins[ip + 3:])
                    self.current_frame().ip += 3

                    err = self.push_closure(const_index, num_free)
                    if err is not None:
                        return err
                case OpCode.OpGetFree:
                    free_index: int = read_uint8(ins[ip + 1:])
                    self.current_frame().ip += 1

                    current_closure = self.current_frame().cl

                    err = self.push(current_closure.free[free_index])
                    if err is not None:
                        return err
                case OpCode.OpCurrentClosure:
                    current_closure = self.current_frame().cl

                    err = self.push(current_closure)
                    if err is not None:
                        return err
                case OpCode.OpLoop:
                    start_loop_offset: int = read_uint16(ins[ip + 1:])
                    self.current_frame().ip -= start_loop_offset


    
    # region VM Helpers
    def push(self, o: Object) -> str:
        return self.stack.push(item=o)

    def pop(self) -> Object:
        return self.stack.pop()
    
    def native_bool_to_boolean_obj(self, input_bool: bool) -> BooleanObject:
        if input_bool:
            return TRUE_OBJ
        return FALSE_OBJ
    
    def is_truthy(self, obj: Object) -> bool:
        match obj.type():
            case "BOOL":
                return obj.value
            case "NULL":
                return False
            case _:
                return True
            
    def current_frame(self) -> Frame:
        return self.frames.items[self.frames.fp - 1]
    
    def push_frame(self, f: Frame):
        self.frames.push(f)
    
    def pop_frame(self) -> Frame:
        return self.frames.pop()
    
    def push_closure(self, const_index: int, num_free: int) -> str:
        constant = self.constants[const_index]
        if not isinstance(constant, CompiledFunction):
            return f"Not a function: {constant}"
        
        free: list[Object] = [None] * num_free
        for i in range(0, num_free, 1):
            free[i] = self.stack.items[self.stack.sp - num_free + i]

        self.stack.sp = self.stack.sp - num_free
        
        closure = ClosureObject(fn=constant, free=free)
        return self.push(closure)
    # endregion

    # region Function Helpers
    def call_closure(self, cl: ClosureObject, num_args: int) -> str:
        if not num_args == cl.fn.num_parameters:
            return f"Wrong number of arguments: want={cl.fn.num_parameters}, got={num_args}"
        
        frame: Frame = Frame(cl=cl, base_pointer=self.stack.sp - num_args)
        self.push_frame(frame)

        self.stack.sp = frame.base_pointer + cl.fn.num_locals

    def call_builtin(self, builtin: Builtin, num_args: int) -> str:
        args = self.stack.items[self.stack.sp - num_args : self.stack.sp]

        result = builtin.fn(*args)
        self.stack.sp = self.stack.sp - num_args - 1

        if result is not None:
            self.push(result)
        else:
            self.push(NULL_OBJ)
    # endregion

    # region VM Builder Helpers
    def build_array(self, start_index: int, end_index: int) -> Object:
        elements: list[Object] = [None] * (end_index - start_index)
        for i in range(start_index, end_index, 1):
            elements[i - start_index] = self.stack.items[i]
        
        return ArrayObject(elements=elements)

    def build_hash(self, start_index: int, end_index: int) -> tuple[Object, str]:
        hashed_pairs: dict[HashKey, HashPair] = {}

        for i in range(start_index, end_index, 2):
            key = self.stack.items[i]
            value = self.stack.items[i + 1]

            pair: HashPair = HashPair(key=key, value=value)

            if not isinstance(key, Hashable):
                return None, f"Unusable as hash key: {key.type()}"
            
            hashed_pairs[key.hash_key()] = pair
        
        return HashObject(pairs=hashed_pairs), None

    # endregion

    # region VM Execution Methods
    def execute_binary_operation(self, op: OpCode) -> str:
        right_obj: Object = self.pop()
        left_obj: Object = self.pop()

        left_type = left_obj.type()
        right_type = right_obj.type()

        if left_type == T_INTEGER_OBJ and right_type == T_INTEGER_OBJ:
            return self.execute_binary_int_operation(op, left_obj, right_obj)
        elif left_type == T_FLOAT_OBJ and right_type == T_FLOAT_OBJ:
            return self.execute_binary_float_operation(op, left_obj, right_obj)
        elif left_type in [T_INTEGER_OBJ, T_FLOAT_OBJ] and right_type in [T_INTEGER_OBJ, T_FLOAT_OBJ]:
            return self.execute_binary_float_operation(op, left_obj, right_obj)
        elif left_type == T_STRING_OBJ and right_type == T_STRING_OBJ:
            return self.execute_binary_string_operation(op, left_obj, right_obj)
        
        return f"Unsupported types for binary operation: {left_type} {right_type}-{right_obj.value}"
    
    def execute_comparison(self, op: OpCode) -> str:
        right_node: Object = self.pop()
        left_node: Object = self.pop()

        if left_node.type() in [T_INTEGER_OBJ, T_FLOAT_OBJ] and right_node.type() in [T_INTEGER_OBJ, T_FLOAT_OBJ]:
            return self.execute_number_comparison(op, left_node, right_node)
        
        match op:
            case OpCode.OpEqual:
                return self.push(self.native_bool_to_boolean_obj(right_node == left_node))
            case OpCode.OpNotEqual:
                return self.push(self.native_bool_to_boolean_obj(right_node != left_node))
            case _:
                return f"Unknown Comparison Operator: {op} ({left_node.type()}, {right_node.type()})"

    def execute_bang_operator(self) -> str:
        operand = self.pop()

        match operand.type():
            case "BOOL":
                operand: BooleanObject = operand
                if operand.value:
                    return self.push(FALSE_OBJ)
                else:
                    return self.push(TRUE_OBJ)
            case "NULL":
                return self.push(TRUE_OBJ)
            case _:
                return self.push(FALSE_OBJ)
            
    def execute_minus_operator(self) -> str:
        operand = self.pop()

        if operand.type() not in [T_INTEGER_OBJ, T_FLOAT_OBJ]:
            return f"Unsupported type for negation: {operand.type()}"
        
        if operand.type() == T_INTEGER_OBJ:
            operand: IntegerObject = operand
            return self.push(IntegerObject(value=-operand.value))
        elif operand.type() == T_FLOAT_OBJ:
            operand: FloatObject = operand
            return self.push(FloatObject(value=-operand.value))
        
    def execute_index_expression(self, left: Object, index: Object) -> str:
        if left.type() == T_ARRAY_OBJ and index.type() == T_INTEGER_OBJ:
            return self.execute_array_index(left, index)
        elif left.type() == T_HASH_OBJ:
            return self.execute_hash_index(left, index)
        else:
            return f"Index operator not supported: {left.type()}"
    
    def execute_call(self, num_args: int) -> str:
        callee = self.stack.items[self.stack.sp - 1 - num_args]
        match callee.type():
            case "CLOSURE":
                return self.call_closure(callee, num_args)
            case "BUILTIN":
                return self.call_builtin(callee, num_args)
            case _:
                return f"calling non-closure or non-builtin"
    # endregion

    # region Binary Operation Helpers
    def execute_binary_int_operation(self, op: OpCode, left: IntegerObject, right: IntegerObject):
        left_value: int = left.value
        right_value: int = right.value

        result: int = None
        
        match op:
            case OpCode.OpAdd:
                result = left_value + right_value
            case OpCode.OpSub:
                result = left_value - right_value
            case OpCode.OpMul:
                result = left_value * right_value
            case OpCode.OpDiv:
                result = left_value / right_value
            case _:
                return f"Unknown integer operator: {op}"
        
        return self.push(IntegerObject(value=result))

    def execute_binary_float_operation(self, op: OpCode, left: FloatObject, right: FloatObject):
        left_value: float = left.value
        right_value: float = right.value

        result: float = None
        
        match op:
            case OpCode.OpAdd:
                result = left_value + right_value
            case OpCode.OpSub:
                result = left_value - right_value
            case OpCode.OpMul:
                result = left_value * right_value
            case OpCode.OpDiv:
                result = left_value / right_value
            case _:
                return f"Unknown integer operator: {op}"
        
        return self.push(FloatObject(value=result))
    
    def execute_binary_string_operation(self, op: OpCode, left: StringObject, right: StringObject) -> str:
        if not op == OpCode.OpAdd:
            return f"Unnown string operator: {op}"
        
        left_value: str = left.value
        right_value: str = right.value

        return self.push(StringObject(value=left_value + right_value))
    # endregion

    # region Comparison Operation Helpers
    def execute_number_comparison(self, op: int, left: FloatObject, right: FloatObject) -> str:
        left_value = left.value
        right_value = right.value

        match op:
            case OpCode.OpEqual:
                return self.push(self.native_bool_to_boolean_obj(right_value == left_value))
            case OpCode.OpNotEqual:
                return self.push(self.native_bool_to_boolean_obj(right_value != left_value))
            case OpCode.OpGreaterThan:
                return self.push(self.native_bool_to_boolean_obj(left_value > right_value))
            case OpCode.OpGreaterThanEqual:
                return self.push(self.native_bool_to_boolean_obj(left_value >= right_value))
            case _:
                return F"Unknown Number Comparison Operator: {op}"
    # endregion

    # region Index Operation Helpers
    def execute_array_index(self, array: ArrayObject, index: IntegerObject) -> str:
        i = index.value
        max_ = len(array.elements) - 1

        if i < 0 or i > max_:
            return self.push(NULL_OBJ)
        
        return self.push(array.elements[i])
    
    def execute_hash_index(self, hash_obj: HashObject, index: Object) -> str:
        if not isinstance(index, Hashable):
            return f"Unusable as hash key: {index.type()}"
        
        pair = hash_obj.pairs.get(index.hash_key())
        if pair is None:
            return self.push(NULL_OBJ)
        
        return self.push(pair.value)
    # endregion