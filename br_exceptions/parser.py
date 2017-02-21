from typing import Dict, List, Tuple

from br_exceptions.base import BaseBrException


class BaseParserException(BaseBrException):
    pass


class ParserArgumentCheckException(BaseParserException):
    def __init__(self,
                 function: 'Function',
                 params: List['Token'],
                 number: int = None,
                 exc: Exception = None
                 ):
        self.function = function
        self.params = params
        self.number = number
        self.exc = exc

    def __str__(self):
        return "Fuck"


class ParserArgumentCheckLenException(ParserArgumentCheckException):
    def __str__(self):
        return "Неверное количество аргументов"


class ParserArgumentCheckTypeException(ParserArgumentCheckException):
    def __str__(self):
        return "Невозможно сопоставить тип"


class ParserFunctionNotFoundException(BaseParserException):
    def __init__(self, token: 'Token'):
        self.token = token

    def __str__(self):
        return "Невозможно найти функцию с именем `{}`".format(
            self.token.text
        )
