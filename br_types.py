import re

from br_exceptions.types import *
from br_lexer import Token
from br_parser import BrFunctionLifeTime


class AbstractBrType:
    type_name = None

    def __init__(self, raw: Token):
        self.token = raw
        self.value = self._parse()

    def _parse(self):
        raise NotImplemented()

    def __str__(self):
        return "Type<{}>:{}".format(self.type_name, self.value)


class IntBrType(AbstractBrType):
    type_name = "int"

    def _parse(self):
        return int(self.token.text)


# Должен стоять последним, так как смотрит все модули выше него
class BrTypeBrType(AbstractBrType):
    _type_name = "type"
    _types = {val: globals()[val] for val in dir()
              if issubclass(globals()[val], AbstractBrType)
              and globals()[val] != AbstractBrType
              }

    def _parse(self):
        type_name = self.token.text
        tp = self._types.get(type_name, None)
        if not tp:
            raise TypeNameErrorException(type_name)
        self.value = tp


class IdentifierBrType(AbstractBrType):
    type_name = "func_name"
    _regexp = re.compile(r'[A-z]\w*')

    def _parse(self):
        name = self.token.text
        match = self._regexp.match(name)
        if not match:
            raise IdentifierNameErrorException(name)
        span = match.span()
        if (span[1] - span[0]) > len(name):
            raise IdentifierNameErrorException(name)
        self.value = name


# Здесь внутренние типы, которые нельзя использовать снаружи
class FunctionLifeTimeBrType(AbstractBrType):
    _type_name = "function_type"
    _values = {i.name: i for i in BrFunctionLifeTime}

    def _parse(self):
        name = self.token.text
        life_time = self._values.get(name, None)
        if not life_time:
            raise FunctionLifeTimeErrorException(name)
        self.value = life_time