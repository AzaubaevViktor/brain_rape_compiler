import abc
from enum import Enum
from typing import List, Dict, Type, TypeVar, Tuple, Any, Iterator

from br_exceptions.parser import ParserArgumentCheckLenException, ParserArgumentCheckTypeException, \
    ParserSymbolNotFoundException, ParserFunctionNotFoundException, \
    ParserVariableNotFoundException, ParserArgumentTypeEqException
from br_exceptions.types import BaseTypesException, IdentifierNameErrorException
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

    def renamed(self, new_name: str) -> 'Variable':
        return Variable(new_name, self.value_type)

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
        return "Argument<{about}>".format(
            about=str(self)
        )

    def __str__(self):
        return "{self.var_type.__name__} {self.name}".format(
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
                 code: List[Expression] or List[List[Expression]] or None = None,
                 builtin: bool = False
                 ):
        self.name = name
        self.arguments = arguments
        self.type = _type
        self.lifetime = lifetime
        self.source = source or []
        self.code = code
        self.builtin = builtin

    def check_args(self,
                   params: List[Token],
                   namespace: 'NameSpace' = None
                   ) -> Dict[str, Variable]:
        variables = {}
        if len(self.arguments) != len(params):
            raise ParserArgumentCheckLenException(
                self,
                params
            )
        # try:
        for arg, var_token in zip(self.arguments, params):
            # maybe var_token is identifer?
            from br_types import IdentifierBrType
            try:
                identifier = IdentifierBrType(var_token)
                variable = namespace.get_var(identifier)
                # При передаче в аргумент другого аргумента
                variable = variable.renamed(arg.name)
                if not isinstance(variable.value_type, arg.var_type):
                    raise ParserArgumentTypeEqException(arg.var_type,
                                                        type(variable.value_type))

            except (ParserVariableNotFoundException,
                    IdentifierNameErrorException):
                # This is not identifier, try to parse directly
                try:
                    variable = arg.apply(var_token)
                except BaseTypesException as e2:
                    raise e2

            variables[arg.name] = variable
        # except Exception as e:
        #     raise ParserArgumentCheckTypeException(
        #         self,
        #         params,
        #         exc=e
        #     )
        # finally:
        #     pass
        return variables

    def compile(self,
                variables: Dict[str, Variable],
                namespace: 'NameSpace' = None
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
                "{name}" \
                "({arguments}); {lines_len} lines inside".format(
            is_builtin="Builtin " if self.builtin else "",
            type=self.type.name.lower(),
            lifetime=self.lifetime.name.lower(),
            name=self.name,
            arguments=", ".join([str(arg) for arg in self.arguments] or ["No Arguments"]),
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

    def get(self, item: Token, default=None) -> Symbol:
        if item.text in self.symbols:
            return self.symbols[item.text]
        elif self.parent:
            return self.parent.get(item, default)
        else:
            return default

    def __getitem__(self, item: Token) -> Symbol:
        symbol = self.get(item, None)
        if symbol:
            return symbol
        else:
            raise ParserSymbolNotFoundException(item)

    def get_vars(self) -> Iterator[Variable]:
        for symbol in self.symbols.values():
            if isinstance(symbol, Variable):
                yield symbol
        if self.parent:
            yield from self.parent.get_vars()

    def get_func(self, token: Token) -> Function:
        func = self.get(token)
        if not isinstance(func, Function):
            raise ParserFunctionNotFoundException(token)
        return func

    def get_var(self, identifier: 'IdentifierBrType'):
        var = self.get(identifier.token)
        if not isinstance(var, Variable):
            raise ParserVariableNotFoundException(identifier.token)
        return var

    def get_address_value(self, addr: 'AddressBrType') -> int:
        val = addr.value
        from br_types import IdentifierBrType
        if isinstance(val, IdentifierBrType):
            return self.get_var(val.token).value
        else:
            return addr.value

    def create_namespace(self):
        ns = NameSpace(self)
        return ns

