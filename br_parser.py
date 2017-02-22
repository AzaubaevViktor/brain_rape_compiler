import abc
from enum import Enum
from typing import List, Dict, Type, TypeVar, Tuple, Any

from br_exceptions.parser import ParserArgumentCheckLenException, ParserArgumentCheckTypeException, \
    ParserSymbolNotFoundException, ParserFunctionNotFoundException, \
    ParserVariableNotFoundException
from br_lexer import Line, Token,  Expression
from bytecode import ByteCode


class Symbol(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        self.name = None


class Variable(Symbol):
    def __init__(self, name: str, value_type: 'AbstractBrType'):
        self.name = name
        self.value_type = value_type

    @property
    def token(self) -> Token:
        return self.value_type.token

    @property
    def value(self) -> Any:
        return self.value_type.value

    def __repr__(self):
        return "Variable<{self.name} = {self.value_type}".format(
            self=self
        )


class Argument:
    """ Аргумент для функции """
    def __init__(self, name: str, var_type: Type['AbstractBrType']):
        self.name = name
        self.var_type = var_type

    def apply(self, token: Token) -> Variable:
        return Variable(self.name, self.var_type(token))

    def __repr__(self):
        return "Argument<{self.var_type.__name__} {self.name}>".format(
            self=self
        )

class FunctionType(Enum):
    NO_BLOCK = 1
    BLOCK = 2


class FunctionLifeTime(Enum):
    GLOBAL = 1  # Текущий namespace и дочерние
    ONLY_CURRENT = 2  # Только этот namespace (Для __main)


class Function(Symbol):
    """ функция """
    def __init__(self,
                 name: str,
                 arguments: List[Argument],
                 _type: FunctionType,
                 lifetime: FunctionLifeTime,
                 source: List[Line] or None = None,
                 code: List[Expression] or Tuple(List[Expression], List[Expression]) or None = None,
                 builtin: bool = False
                 ):
        self.name = name
        self.arguments = arguments
        self.type = _type
        self.lifetime = lifetime
        self.source = source or []
        self.code = code
        self.builtin = builtin

    def check_args(self, params: List[Token]) -> Dict[str, Variable]:
        variables = {}
        if len(self.arguments) != len(params):
            raise ParserArgumentCheckLenException(
                self,
                params
            )
        try:
            for arg, var in zip(self.arguments, params):
                variables[arg.name] = arg.apply(var)
        except Exception as e:
            raise ParserArgumentCheckTypeException(
                self,
                params,
                exc=e
            )
        return variables

    def compile(self,
                variables: Dict[str, Variable]
                ) -> List[ByteCode]:
        return NotImplemented

    def compile_block(self,
                      variables: Dict[str, Variable],
                      block_inside: List[Expression] or None = None,
                      namespace: 'NameSpace' = None
                      ) -> List[ByteCode]:
        return NotImplemented

    def __str__(self):

        lines_len = len(self.source)

        about = "{is_builtin}" \
                "{lifetime} " \
                "{type} " \
                "Function " \
                "`{name}`: " \
                "{arguments}; {lines_len} lines inside".format(
            is_builtin="Builtin " if self.builtin else "",
            type=self.type.name.lower(),
            lifetime=self.lifetime.name.lower(),
            name=self.name,
            arguments=self.arguments,
            lines_len=lines_len
        )
        return about


class NameSpace:
    def __init__(self, parent: 'NameSpace' or None):
        self.parent = parent  # type: NameSpace
        self.symbols = {}

    def symbol_push(self, symbol: Symbol):
        self.symbols[symbol.name] = symbol

    def symbols_push(self, symbols: List[Symbol]):
        for symbol in symbols:
            self.symbol_push(symbol)

    def __getitem__(self, item: Token) -> Symbol:
        if item.text in self.symbols:
            return self.symbols[item.text]
        elif self.parent:
            return self.parent[item]
        else:
            raise ParserSymbolNotFoundException(item)

    def get_func(self, token: Token) -> Function:
        func = self[token]
        if not isinstance(func, Function):
            raise ParserFunctionNotFoundException(token)
        return func

    def get_var(self, token: Token):
        var = self[token]
        if not isinstance(var, Variable):
            raise ParserVariableNotFoundException(token)
        return var

    def create_namespace(self):
        ns = NameSpace(self)
        return ns

