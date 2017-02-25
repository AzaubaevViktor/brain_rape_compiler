import abc
import re
from typing import Any

from br_exceptions.types import *
from br_lexer import Token
from br_parser import FunctionLifeTime


class AbstractBrType(metaclass=abc.ABCMeta):
    """ Умеет парсить и хранить в себе значение определённого типа """
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
            try:
                self._parse()
            except BaseTypesException as e:
                e.token = self.token
                raise e

    @abc.abstractclassmethod
    def _parse(self):
        pass

    def __str__(self):
        return "Type<{}>:{}".format(self.name, self.value)


class IntBrType(AbstractBrType):
    name = "int"

    def _parse(self):
        try:
            self.value = int(self.token.text)
        except ValueError:
            IntParseException(self.token)


class IdentifierBrType(AbstractBrType):
    name = "identifier"
    _regexp = re.compile(r'[A-z]\w*')

    def _parse(self):
        match = self._regexp.match(self.text)
        if not match:
            raise IdentifierNameErrorException(self.token)
        span = match.span()
        if (span[1] - span[0]) > len(self.text):
            raise IdentifierNameErrorException(self.token)
        self.value = self.text


class AddressBrType(AbstractBrType):
    name = "address"
    _addr_int_r = re.compile(r':(\d+)')

    def _parse(self):
        # try to find `:123...`
        match = self._addr_int_r.match(self.text)
        if not match:
            raise IdentifierNameErrorException(self.token)
        span = match.span()
        if (span[1] - span[0]) > len(self.text):
            raise IdentifierNameErrorException(self.token)
        self.value = int(self.text[1:])


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
            raise FunctionLifeTimeErrorException(name)
        self.value = life_time
