from br_exceptions.base import BaseBrException


class BaseLexerException(BaseBrException):
    pass


class LexerLevelErrorException(BaseLexerException):
    def __init__(self, s, level):
        self.s = s
        self.level = level

    def __str__(self):
        return "Неверное количество пробелов. Оно должно быть кратно 4м"
