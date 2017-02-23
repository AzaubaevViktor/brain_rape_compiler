from br_lexer import Token
from br_parser import Variable
from br_types import AddressBrType

builtin_variables = [
    Variable('first', AddressBrType(Token(-1, -1, ":1")))
]
