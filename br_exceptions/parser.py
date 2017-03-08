from typing import List

from br_exceptions.base import Base


class BaseParserException(Base):
    pass


class ParserArgumentCheckException(BaseParserException):
    def __init__(self,
                 function: 'BrFunction',
                 params: List['Token'],
                 number: int = None,
                 exc: Exception = None
                 ):
        self.function = function
        self.params = params
        self.number = number  # for functions with variative len
        self.exc = exc

    def __str__(self):
        return "Fuck"


class ParserArgumentCheckLenException(ParserArgumentCheckException):
    def __str__(self):
        return "Неверное количество аргументов для " \
               "функции `{func.name}`. Ожидается {expect}, " \
               "передано `{passed}`".format(
            func=self.function,
            expect=len(self.function.arguments) or self.number,
            passed=len(self.params)
        )


class ParserArgumentCheckTypeException(ParserArgumentCheckException):
    def __str__(self):

        return "Невозможно сопоставить тип, ошибка:\n====\n" \
               "{}\n" \
               "{}".format(type(self.exc), self.exc)


class ParserArgumentTypeEqException(BaseParserException):
    def __init__(self,
                 type1: 'BrType',
                 type2: 'BrType'
                 ):
        self.type1 = type1
        self.type2 = type2

    def __str__(self):
        return "Несовместимые типы. " \
               "Ожидается {}, " \
               "передано {}".format(
            self.type1,
            self.type2
        )


class ParserSymbolNotFoundException(BaseParserException):
    _what = "символ"

    def __init__(self, token: 'Token'):
        self.token = token

    def __str__(self):
        return "Невозможно найти {} с именем `{}`".format(
            self._what,
            self.token.text
        )


class ParserFunctionNotFoundException(ParserSymbolNotFoundException):
    _what = "функцию"


class ParserVariableNotFoundException(ParserSymbolNotFoundException):
    _what = "переменную"
