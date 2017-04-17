import abc
import re

from br_lexer import Token
from .excs.types import IntTypeError, AddressTypeError

from .excs.base import ParserException


class AbstractType(metaclass=abc.ABCMeta):
    name = "__abstract__"

    def __init__(self, token: Token):
        self.token = token
        try:
            self.value = self._parse(self.token.text)
        except ParserException as e:
            e.place = token
            raise e

    @classmethod
    @abc.abstractmethod
    def _parse(cls, text: str) -> object:
        """ Превращает текст токена в значение """
        pass


class IntType(AbstractType):
    name = "int"

    @classmethod
    def _parse(cls, text: str) -> object:
        try:
            return int(text)
        except ValueError:
            raise IntTypeError(None, None)


class AbstractRegexType(AbstractType):
    name = "__abstract_regexp__"
    regexp = re.compile(r'')
    exception_class = ParserException

    @classmethod
    @abc.abstractmethod
    def _process(cls, text: str) -> object:
        """ Превращает распознаный текст из регулярного выражения в значение"""
        pass

    @classmethod
    def _parse(cls, text: str) -> object:
        match = cls.regexp.match(text)
        if not match:
            raise cls.exception_class(None, None)
        span = match.span()
        if (span[1] - span[0]) > len(text):
            raise cls.exception_class(None)
        return cls._process(match.groups()[0])


class AddressType(AbstractRegexType):
    name = "address"
    regexp = re.compile(r':(\d+)')
    exception_class = AddressTypeError

    @classmethod
    def _process(cls, text: str):
        return int(text)
