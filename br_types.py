import abc
import re
from typing import Any

from br_exceptions.types import *
from br_lexer import Token
from br_parser import FunctionLifeTime


class AbstractBrType(metaclass=abc.ABCMeta):
    """ Умеет парсить и хранить в себе значение определённого типа """
    name = None

    def __init__(self, raw: Token):
        self.token = raw
        try:
            self.value = self._parse(raw)
        except BaseTypesException as e:
            e.token = self.token
            raise e

    @classmethod
    @abc.abstractclassmethod
    def _parse(cls, text) -> Any:
        pass

    def __str__(self):
        return "Type<{}>:{}".format(self.name, self.value)


class IntBrType(AbstractBrType):
    name = "int"

    @classmethod
    def _parse(cls, token: Token):
        text = token.text
        return int(text)


class IdentifierBrType(AbstractBrType):
    name = "identifier"
    _regexp = re.compile(r'[A-z]\w*')

    @classmethod
    def _parse(cls, token: Token):
        text = token.text
        match = cls._regexp.match(text)
        if not match:
            raise IdentifierNameErrorException(text)
        span = match.span()
        if (span[1] - span[0]) > len(text):
            raise IdentifierNameErrorException(text)
        return text


class AddressBrType(AbstractBrType):
    name = "address"
    _regexp = re.compile(r':(\d+)')

    def _parse(cls, token: Token) -> int or IdentifierBrType:
        text = token.text
        # try to find `:123...`
        try:
            match = cls._regexp.match(text)
            if not match:
                raise IdentifierNameErrorException(text)
            span = match.span()
            if (span[1] - span[0]) > len(text):
                raise IdentifierNameErrorException(text)
            return int(text[1:])
        except Exception:
            try:
                data = IdentifierBrType(token)
            except Exception as e:
                raise e
            return data


# Должен стоять последним, так как смотрит все модули выше него
class BrTypeBrType(AbstractBrType):
    _type_name = "type"
    _types = {cl.name: cl for name, cl in globals().items()
              if isinstance(cl, type) and
              issubclass(cl, AbstractBrType)
              and cl != AbstractBrType
              }

    @classmethod
    def _parse(cls,  token: Token):
        type_name = token.text
        tp = cls._types.get(type_name, None)
        if not tp:
            raise TypeNameErrorException(type_name)
        return tp

# Здесь внутренние типы, которые нельзя использовать в программе


class FunctionLifeTimeBrType(AbstractBrType):
    _type_name = "function_type"
    _values = {i.name.lower(): i for i in FunctionLifeTime}

    @classmethod
    def _parse(cls, token: Token):
        name = token.text
        life_time = cls._values.get(name, None)
        if not life_time:
            raise FunctionLifeTimeErrorException(name)
        return life_time
