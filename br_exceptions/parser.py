from typing import List

from br_exceptions.base import BaseBrException


class BaseParserException(BaseBrException):
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
            expect=len(self.function.arguments or self.number),
            passed=len(self.params)
        )


class ParserArgumentCheckTypeException(ParserArgumentCheckException):
    def __str__(self):

        return "Невозможно сопоставить тип, ошибка:\n====\n" \
               "{}\n" \
               "{}".format(type(self.exc), self.exc)


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
