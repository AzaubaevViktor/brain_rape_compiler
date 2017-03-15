import abc
import re
from typing import Any

from br_exceptions.types import *
from br_lexer import Token
from br_parser import FunctionLifeTime


class AbstractBrType(metaclass=abc.ABCMeta):
    """
    Тип.
    Представляет собой парсер, который при передаче токена в него
    определяет значение этого типа.
    """
    name = None

    def __init__(self, token: Token,
                 value: Any = None):
        self.token = token  # Текст, представляющий тип
        if self.token:
            self.text = self.token.text
        else:
            self.text = "Token not found, maybe builtin definision?"
        self.value = value  # значение типа
        if self.value is None:
            self._parse()

    @abc.abstractclassmethod
    def _parse(self):
        pass

    def __str__(self):
        return "(T{}):`{}`".format(self.name, self.value)


class IntBrType(AbstractBrType):
    name = "int"

    def _parse(self):
        try:
            self.value = int(self.token.text)
        except ValueError:
            IntParseException(self.token)


class _RegexprBrType(AbstractBrType):
    regexp = re.compile(r'')
    exception_class = BaseTypesException

    def _parse(self):
        match = self.regexp.match(self.text)
        if not match:
            raise self.exception_class(self.token)
        span = match.span()
        if (span[1] - span[0]) > len(self.text):
            raise self.exception_class(self.token)
        self.value = match.groups()[0]


class StrBrType(_RegexprBrType):
    name = 'str'
    regexp = re.compile(r'"(.*)"')
    exception_class = StrParseException


class IdentifierBrType(_RegexprBrType):
    name = "identifier"
    regexp = re.compile(r'([A-z]\w*)')
    exception_class = IdentifierNameErrorException


class AddressBrType(_RegexprBrType):
    name = "address"
    regexp = re.compile(r':(\d+)')

    def _parse(self):
        super()._parse()
        self.value = int(self.value)


# Должен стоять последним, так как смотрит все модули выше него
class BrTypeBrType(AbstractBrType):
    _type_name = "type"
    _types = {cl.name: cl for name, cl in globals().items()
              if isinstance(cl, type) and
              issubclass(cl, AbstractBrType)
              and cl != AbstractBrType
              }

    def _parse(self):
        type_name = self.text
        tp = self._types.get(type_name, None)
        if not tp:
            raise TypeNameErrorException(self.token)
        self.value = tp

# Здесь внутренние типы, которые нельзя использовать в программе


class FunctionLifeTimeBrType(AbstractBrType):
    _type_name = "function_type"
    # TODO: Разобраться с этим говном
    _values = {i.name.lower(): i for i in FunctionLifeTime}

    def _parse(self):
        name = self.text
        life_time = self._values.get(name, None)
        if not life_time:
            raise FunctionLifeTimeErrorException(self.token)
        self.value = life_time
