from br_exceptions.base import Base


class _BaseLexer(Base):
    pass


class LevelError(_BaseLexer):
    def __init__(self, line: 'Line'):
        self.line = line

    def __str__(self):
        return "\n" \
               "Неверное количество пробелов. Оно должно быть кратно 4м\n" \
               "{self.line.line_n}: `{self.line.source}`".format(
            self=self
        )


class BlockLevelError(_BaseLexer):
    def __init__(self, prev_line: 'Line',
                 cur_line: 'Line'):
        self.prev_line = prev_line
        self.cur_line = cur_line

    def __str__(self):
        return "Неверная последовательность уровней вложенности:\n" \
               "{prev_line.line_n}: `{prev_line.source}`\n" \
               "{cur_line.line_n}: `{cur_line.source}`\n" \
               "Уровень `{prev_line.level}` перед уровнем `{cur_line.level}`" \
               " в строке `{cur_line.line_n}`".format(
            prev_line=self.prev_line,
            cur_line=self.cur_line
        )
