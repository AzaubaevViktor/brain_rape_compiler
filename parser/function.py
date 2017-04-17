import abc
from typing import List, Type, TypeVar, Dict

from br_lexer import Token, Expression
from bytecode import ByteCode
from .enums import FunctionTypes, LifeTime
from .types import AbstractType


class Symbol:
    def __init__(self, name, *args, **kwargs):
        self.name = name


class Variable(Symbol):
    def __init__(self, name: str, value_instance: AbstractType):
        super().__init__(name)
        self.value_instance = value_instance

    @property
    def type(self):
        return self.value_instance.__class__

    @property
    def value(self):
        return self.value_instance.value

class Argument:
    def __init__(self, name: str, arg_type: TypeVar[AbstractType]):
        self.name = name
        self.arg_type = arg_type

    def get_var(self, token):
        return Variable(
            self.name,
            self.arg_type(token)
        )


class Function(metaclass=abc.ABCMeta):
    name = ""  # type: str
    arguments = []  # type: List[Argument]
    source = []  # type: List[Expression]
    _code = []  # type: List[ByteCode]

    function_type = FunctionTypes.NOBLOCK  # type: FunctionTypes
    lifetime = LifeTime.LOCAL  # type: LifeTime
    builtin = False

    def __init__(self,
                 context,
                 argument_tokens: List[Token],
                 code_inside: List[ByteCode] = None
                 ):
        self.variables = self._parse_arguments(argument_tokens)
        self.code_inside = code_inside

    @classmethod
    def _parse_arguments(cls, argument_tokens: List[Token]) -> Dict[str, Variable]:
        arguments = {}
        for arg, arg_token in zip(cls.arguments, argument_tokens):
            # try parse directly
            arguments[arg.name] = arg.get_var(arg_token)
            # if not -- find symbol from context
            pass

        return arguments

    @property
    @abc.abstractmethod
    def code(self) -> List[ByteCode]:
        pass

