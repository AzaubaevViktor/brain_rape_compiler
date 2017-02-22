import abc
import re

from br_exceptions.types import *
from br_lexer import Token
from br_parser import FunctionLifeTime


class AbstractBrType(metaclass=abc.ABCMeta):

    type_name = None

    def __init__(self, raw: Token):
        self.token = raw
        self.value = self._parse(raw.text)

    @classmethod
    @abc.abstractclassmethod
    def _parse(cls, text):
        pass

    def __str__(self):
        return "Type<{}>:{}".format(self.type_name, self.value)


class IntBrType(AbstractBrType):
    type_name = "int"

    @classmethod
    def _parse(cls, text):
        return int(text)


# Должен стоять последним, так как смотрит все модули выше него
class BrTypeBrType(AbstractBrType):
    _type_name = "type"
    _types = {name: cl for name, cl in globals().items()
              if type(cl) == type and
              issubclass(cl, AbstractBrType)
              and cl != AbstractBrType
              }

    @classmethod
    def _parse(cls, text):
        type_name = text
        tp = cls._types.get(type_name, None)
        if not tp:
            raise TypeNameErrorException(type_name)
        return tp


# Здесь внутренние типы, которые нельзя использовать в программе
class IdentifierBrType(AbstractBrType):
    type_name = "func_name"
    _regexp = re.compile(r'[A-z]\w*')

    @classmethod
    def _parse(cls, text):
        name = text
        match = cls._regexp.match(name)
        if not match:
            raise IdentifierNameErrorException(name)
        span = match.span()
        if (span[1] - span[0]) > len(name):
            raise IdentifierNameErrorException(name)
        return name


class FunctionLifeTimeBrType(AbstractBrType):
    _type_name = "function_type"
    _values = {i.name: i for i in FunctionLifeTime}

    @classmethod
    def _parse(cls, text):
        name = text
        life_time = cls._values.get(name, None)
        if not life_time:
            raise FunctionLifeTimeErrorException(name)
        return life_time
