import abc
from enum import Enum
from typing import List, Dict, Type, TypeVar, Tuple, Any, Iterator, Iterable, T

from br_exceptions import parser as parser_e

from br_exceptions.types import BaseTypesError, IdentifierNameError
from br_lexer import Line, Token, Expression
from bytecode import ByteCode


class Symbol(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        self.name = None


class Variable(Symbol):
    """
    Переменная. Хранит название переменной и экземпляр типа
    """
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
        return "Var<{self.name} = {self.value_type}>".format(
            self=self
        )


class Argument:
    """
    Аргумент для функции
    Представляет собой имя будущей переменной и класс-наследник типа
    Служит для обработки токенов, переданных в функцию
    """

    def __init__(self, name: str, value_class: Type['AbstractBrType']):
        self.name = name
        self.value_class = value_class

    def get_var(self, token: Token) -> Variable:
        return Variable(self.name, self.value_class(token))

    def __repr__(self):
        return "Argument<{about}>".format(
            about=str(self)
        )

    def __str__(self):
        return "{self.value_class.name} {self.name}".format(
            self=self
        )


class FunctionType(Enum):
    NO_BLOCK = 1
    BLOCK = 2


class LifeTime(Enum):
    GLOBAL = 1  # Глобальный NameSpace
    LOCAL = 2  # Текущий и дочерние NameSpace
    # INSIDE = 3  # Только текущий NameSpace


class Function(Symbol):
    """ функция """
    def __init__(self,
                 name: str,
                 arguments: List[Argument],
                 _type: FunctionType,
                 lifetime: LifeTime,
                 source: List[Line] or None = None,
                 code: List[Expression] or None = None,
                 builtin: bool = False
                 ):
        self.name = name
        self.arguments = arguments
        self.type = _type
        self.lifetime = lifetime
        self.source = source or []
        self.code = code
        self.builtin = builtin

    def check_args(self, context: 'Context') -> Dict[str, Variable]:
        variables = {}
        tokens = context.expr.args
        if len(self.arguments) != len(tokens):
            raise parser_e.ArgumentLenError(
                context,
                token=tokens[len(self.arguments)]
            )

        from br_types import IdentifierBrType

        error_arg_token = None
        try:
            for arg, arg_token in zip(self.arguments, tokens):  # type: Tuple[Argument, Token]
                error_arg_token = arg_token
                try:
                    variable = arg.get_var(arg_token)
                except BaseTypesError as bte:
                    try:
                        identifier = IdentifierBrType(arg_token)
                    except BaseTypesError as ie:
                        raise parser_e.ArgumentParseError(bte, ie)

                    variable = context.ns.get_var(identifier)  # type: Variable
                    # При передаче в аргумент другого аргумента
                    variable = variable.renamed(arg.name)
                    if not isinstance(variable.value_type, arg.value_class):
                        raise parser_e.ArgumentCheckTypeError(
                            arg.value_class,
                            type(variable.value_type))

                variables[arg.name] = variable
        except Exception as e:
            e.context = context
            e.token = error_arg_token
            raise e
        finally:
            pass
        return variables

    def compile(self, context: 'Context') -> List[ByteCode]:
        return NotImplemented

    def compile_block(self, context: 'Context') -> List[ByteCode]:
        return NotImplemented

    @property
    def file_name(self):
        return self.source[0].file_name

    def __str__(self):

        lines_len = len(self.source)

        about = "{line_n}: " \
                "{is_builtin}" \
                "{lifetime} " \
                "{type} " \
                "Function " \
                "{name}" \
                "({arguments}); {lines_len} lines inside".format(
            line_n=self.source[0].line_n if self.source else "!!",
            is_builtin="Builtin " if self.builtin else "",
            type=self.type.name.lower(),
            lifetime=self.lifetime.name.lower(),
            name=self.name,
            arguments=", ".join(
                [str(arg) for arg in self.arguments] or ["No Arguments"]),
            lines_len=lines_len
        )
        return about


class NameSpace:
    def __init__(self, parent: 'NameSpace' or None = None):
        self.parent = parent  # type: NameSpace
        self.symbols = {}
        self.code_inceptions = {}  # type: Dict[str, List[ByteCode]]

    def add_code_inception(self,
                           func_name: str,
                           bytecode: List[ByteCode]
                           ):
        self.code_inceptions[func_name] = bytecode

    def get_code_inception(self,
                           func_name: str
                           ) -> List[ByteCode]:
        if func_name not in self.code_inceptions:
            if self.parent:
                return self.parent.get_code_inception(func_name)
            else:
                raise parser_e.CodeInceptionNotFound(
                    context=self,
                    token=func_name
                )
        else:
            return self.code_inceptions[func_name]

    def symbol_push(self, symbol: Symbol, lifetime: LifeTime = None):
        lifetime = lifetime or LifeTime.LOCAL

        if LifeTime.LOCAL:
            self.symbols[symbol.name] = symbol

    def symbols_push(self, symbols: Iterable[Symbol]):
        for symbol in symbols:
            self.symbol_push(symbol)

    def get(self, item: Token, default=None) -> Symbol:
        if item.text in self.symbols:
            return self.symbols[item.text]
        else:
            return default

    def __getitem__(self, item: Token) -> Symbol:
        symbol = self.get(item, None)
        if symbol:
            return symbol
        else:
            raise parser_e.SymbolNotFoundException(item)

    def get_vars(self) -> Iterator[Variable]:
        for symbol in self.symbols.values():
            if isinstance(symbol, Variable):
                yield symbol

    def get_func(self, token: Token) -> Function:
        func = self.get(token)
        if not isinstance(func, Function):
            raise parser_e.FunctionNotFoundError(token)
        return func

    def get_var(self, identifier: 'IdentifierBrType') -> Variable:
        var = self.get(identifier.token)
        if not isinstance(var, Variable):
            raise parser_e.VariableNotFoundError(identifier.token)
        return var

    def get_address_value(self, addr: 'AddressBrType') -> int:
        val = addr.value
        from br_types import IdentifierBrType
        if isinstance(val, IdentifierBrType):
            return self.get_var(val.token).value
        else:
            return addr.value

    def create_namespace(self) -> 'NameSpace':
        ns = NameSpace(self)
        return ns
