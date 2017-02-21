from br_exceptions.base import BaseBrException


class BaseLexerException(BaseBrException):
    pass


class LexerLevelErrorException(BaseLexerException):
    def __init__(self, s: str, level: int):
        self.s = s
        self.level = level

    def __str__(self):
        return "Неверное количество пробелов. Оно должно быть кратно 4м"


class LexerBlockLevelErrorException(BaseLexerException):
    def __init__(self, prev_line: 'Line',
                 cur_line: 'Line'):
        self.prev_line = prev_line
        self.cur_line = cur_line

    def __str__(self):
        return "Неверная последовательность уровней вложенности:" \
               "`{prev_line.level}` перед `{cur_line.level}`" \
               " в строке `{cur_line.line_n}`".format(
            prev_line=self.prev_line,
            cur_line=self.cur_line
        )