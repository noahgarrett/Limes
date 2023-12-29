from enum import Enum

class TokenType(Enum):
    # Special Tokens
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"

    # Literals
    IDENT = "IDENT"
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"

    # Operators
    PLUS = "+"
    MINUS = "-"
    ASTERISK = "*"
    SLASH = "/"
    MODULUS = "%"
    POW = "^"
    BANG = "!"
    
    # Assignment
    ASSIGN = '='

    # Comparison
    LT = '<'
    GT = '>'
    EQ = '=='
    NOT_EQ = '!='
    LT_EQ = '<='
    GT_EQ = '>='

    # Symbols
    SEMICOLON = ";"
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    COMMA = ","
    LBRACKET = "["
    RBRACKET = "]"
    COLON = ":"

    # Keywords
    FUNCTION = "FUNCTION"
    LET = "LET"
    TRUE = "TRUE"
    FALSE = "FALSE"
    IF = "IF"
    ELSE = "ELSE"
    RETURN = "RETURN"
    IMPORT = "IMPORT"
    WHILE = "WHILE"
    FOR = "FOR"

class Token:
    def __init__(self, token_type: TokenType, literal: str | None) -> None:
        self.type: TokenType = token_type
        self.literal: str | None = literal

    def __str__(self) -> str:
        return f"[{self.type}:{self.literal}]"


KEYWORDS: dict[str, TokenType] = {
    "fn": TokenType.FUNCTION,
    "let": TokenType.LET,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
    "import": TokenType.IMPORT,
    "while": TokenType.WHILE,
    "for": TokenType.FOR
}

GENZ_KEYWORDS: dict[str, TokenType] = {
    "lit": TokenType.LET,
    "be": TokenType.ASSIGN,
    "rn": TokenType.SEMICOLON,
    "nocap": TokenType.TRUE,
    "cap": TokenType.FALSE,
    "sus": TokenType.IF,
    "imposter": TokenType.ELSE
}

def lookup_ident(ident: str) -> TokenType:
    tt: TokenType | None = KEYWORDS.get(ident)
    if tt is not None:
        return tt
    
    tt: TokenType | None = GENZ_KEYWORDS.get(ident)
    if tt is not None:
        return tt
    
    return TokenType.IDENT
