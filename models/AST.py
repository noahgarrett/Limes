from abc import ABC, abstractmethod
from models.Token import Token

class Node(ABC):
    @abstractmethod
    def token_literal(self) -> str:
        pass

    @abstractmethod
    def string(self) -> str:
        pass

    @abstractmethod
    def type(self) -> str:
        pass


class Statement(Node):
    pass

class Expression(Node):
    pass

class Program(Node):
    def __init__(self) -> None:
        self.statements: list[Statement] = []
    
    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ""
        
    def string(self) -> str:
        output: str = ""
        for s in self.statements:
            output += f"{s.string()}\n"
        
        return output
    
    def type(self) -> str:
        return "Program"
    

# region Statements
class ExpressionStatement(Statement):
    def __init__(self, token: Token, expr: Expression = None) -> None:
        self.token: Token = token
        self.expr: Expression = expr

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        if self.expr is not None:
            return self.expr.string()
        
        return ""
    
    def type(self) -> str:
        return "ExpressionStatement"
    
class AssignStatement(Statement):
    def __init__(self, token: Token, left_value: Expression, right_value: Expression = None) -> None:
        self.token = token
        self.left_value: Expression = left_value
        self.right_value: Expression = right_value
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return f"{self.left_value} = {self.right_value}"
    
    def type(self) -> str:
        return "AssignStatement"
    
class LetStatement(Statement):
    def __init__(self, token: Token, name, value: Expression) -> None:
        self.token = token
        self.name: IdentifierLiteral = name
        self.value = value

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += f"{self.token_literal()} "
        output += self.name.string()
        output += " = "

        if self.value is not None:
            output += self.value.string()
        
        output += ";"

        return output
    
    def type(self) -> str:
        return "LetStatement"
    
class ImportStatement(Statement):
    def __init__(self, token: Token, file_path: str = None) -> None:
        self.token = token
        self.file_path = file_path

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return f"<Import {self.file_path}>"

    def type(self) -> str:
        return "ImportStatement"
    
class BlockStatement(Statement):
    def __init__(self, token: Token, statements: list[Statement] = None) -> None:
        self.token = token
        self.statements = statements if statements is not None else []

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        for stmt in self.statements:
            output += stmt.string()
        
        return output
    
    def type(self) -> str:
        return "BlockStatement"
    
class ReturnStatement(Statement):
    def __init__(self, token: Token, return_value: Expression = None) -> None:
        self.token = token
        self.return_value = return_value
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += f"{self.token_literal()} "

        if self.return_value is not None:
            output += self.return_value.string()

        output += ";"
        return output
    
    def type(self) -> str:
        return "ReturnStatement"
    
class WhileStatement(Statement):
    def __init__(self, token: Token, condition: Expression = None, body: BlockStatement = None) -> None:
        self.token = token
        self.condition = condition
        self.body = body

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += "while "
        output += self.condition.string()
        output += " "
        output += self.body.string()

        return output
    
    def type(self) -> str:
        return "WhileStatement"
# endregion

# region Expressions
class PrefixExpression(Expression):
    def __init__(self, token: Token, operator: str, right_node: Expression = None) -> None:
        self.token: Token = token  # The prefix token ('!' or '-')
        self.operator: str = operator
        self.right_node: Expression = right_node

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += "("
        output += self.operator
        output += self.right_node.string()
        output += ")"

        return output
    
    def type(self) -> str:
        return "PrefixExpression"

class InfixExpression(Expression):
    def __init__(self, token: Token, left_node: Expression, operator: str, right_node: Expression = None) -> None:
        self.token: Token = token
        self.left_node: Expression = left_node
        self.operator: str = operator
        self.right_node: Expression = right_node

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += "("
        output += self.left_node.string()
        output += f" {self.operator} "
        output += self.right_node.string()
        output += ")"

        return output
    
    def type(self) -> str:
        return "InfixExpression"
    
class IfExpression(Expression):
    def __init__(self, token: Token, condition: Expression = None, consequence: BlockStatement = None, alternative: BlockStatement = None) -> None:
        self.token = token
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += "if"
        output += self.condition.string()
        output += " "
        output += self.consequence.string()

        if self.alternative is not None:
            output += "else "
            output += self.alternative.string()
        
        return output
    
    def type(self) -> str:
        return "IfExpression"
    
class CallExpression(Expression):
    def __init__(self, token: Token, function: Expression = None, arguments: list[Expression] = None) -> None:
        self.token = token
        self.function = function
        self.arguments = arguments
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        args: list[str] = []
        for a in self.arguments:
            args.append(a.string())
        
        output += self.function.string()
        output += "("
        output += ",".join(args)
        output += ")"

        return output
    
    def type(self) -> str:
        return "CallExpression"
    
class IndexExpression(Expression):
    def __init__(self, token: Token, left: Expression = None, index: Expression = None) -> None:
        self.token = token
        self.left = left
        self.index = index

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += "("
        output += self.left.string()
        output += "["
        output += self.index.string()
        output += "])"
        return output
    
    def type(self) -> str:
        return "IndexExpression"
# endregion

# region Literals
class IntegerLiteral(Expression):
    def __init__(self, token: Token, value: int = None) -> None:
        self.token: Token = token
        self.value: int = value

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return self.token.literal
    
    def type(self) -> str:
        return "IntegerLiteral"
    
class FloatLiteral(Expression):
    def __init__(self, token: Token, value: float = None) -> None:
        self.token: Token = token
        self.value: float = value

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return self.token.literal
    
    def type(self) -> str:
        return "FloatLiteral"
    
class StringLiteral(Expression):
    def __init__(self, token: Token, value: str = None) -> None:
        self.token = token
        self.value = value
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return self.token.literal
    
    def type(self) -> str:
        return "StringLiteral"
    
class IdentifierLiteral(Expression):
    def __init__(self, token: Token, value: str = None) -> None:
        self.token = token
        self.value = value

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return self.value
    
    def type(self) -> str:
        return "IdentifierLiteral"
    
class BooleanLiteral(Expression):
    def __init__(self, token: Token, value: bool = False) -> None:
        self.token = token
        self.value = value
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return self.token.literal
    
    def type(self) -> str:
        return "BooleanLiteral"
    
class ArrayLiteral(Expression):
    def __init__(self, token: Token, elements: list[Expression] = None) -> None:
        self.token = token
        self.elements: list[Expression] = [] if elements is None else elements

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        elements: list[str] = [el.string() for el in self.elements]

        output += "["
        output += ",".join(elements)
        output += "]"
        return output

    def type(self) -> str:
        return "ArrayLiteral"
    
class HashLiteral(Expression):
    def __init__(self, token: Token, pairs: dict[Expression, Expression] = None) -> None:
        self.token = token
        self.pairs = {} if pairs is None else pairs
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        pairs: list[str] = []
        for key, value in self.pairs.items():
            pairs.append(f"{key.string()}: {value.string()}")
        
        output += "{"
        output += ", ".join(pairs)
        output += "}"
        return output
    
    def type(self) -> str:
        return "HashLiteral"
    
class FunctionLiteral(Expression):
    def __init__(self, token: Token, parameters: list[IdentifierLiteral] = None, body: BlockStatement = None, name: str = "") -> None:
        self.token = token
        self.parameters = parameters
        self.body = body
        self.name: str = name

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        params: list[str] = []
        for p in self.parameters:
            params.append(p.string())
        
        output += self.token_literal()
        if not self.name == "":
            output += f"<{self.name}>"
        output += "("
        output += ",".join(params)
        output += ") "
        output += "{ "
        output += self.body.string()
        output += " }"
        
        return output
    
    def type(self) -> str:
        return "FunctionLiteral"
# endregion
