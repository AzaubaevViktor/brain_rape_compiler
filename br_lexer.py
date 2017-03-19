import abc
from typing import List
from br_exceptions import lexer as lexer_e


class Token:
    def __init__(self, line: 'Line', pos: int, text: str):
        self.line = line
        self.pos = pos
        self.text = text

    def __repr__(self):
        return "{}:{}<{}>".format(self.line.line_n or "?", self.pos, self.text)

    def __str__(self):
        return "{}".format(self.text)

    def __len__(self):
        return len(self.text)


class Expression(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def func_token(self) -> Token:
        pass

    @property
    @abc.abstractmethod
    def args(self) -> List[Token]:
        pass

    @property
    @abc.abstractmethod
    def level(self) -> int:
        pass


class Line(Expression):
    def __init__(self,
                 line_n: int,
                 source: str):
        self.line_n = line_n
        self._level = None  # type: int
        self.tokens = []  # type: List[Token]
        self.source = source.rstrip()

        self._calc_level()
        self._calc_tokens()

    def _calc_level(self):
        """ Подсчитывает уровень вложенности строки """
        level = 0
        for ch in self.source:
            if ' ' == ch:
                level += 1
            else:
                break
        if level % 4:
            raise lexer_e.LevelError(self)
        self._level = level // 4

    def _calc_tokens(self):
        """ Возвращает список токенов из строки """
        pos = 0
        for word in self.source.split(" "):
            if len(word.strip()):
                # Комментарии отсекаем
                if '#' == word[0]:
                    break
                self.tokens.append(Token(self, pos, word.strip()))
                pos += len(word)

            pos += 1

    @property
    def func_token(self) -> Token:
        return self.tokens[0]

    @property
    def args(self) -> List[Token]:
        return self.tokens[1:]

    @property
    def level(self) -> int:
        return self._level

    def __bool__(self):
        return len(self.tokens) > 0

    def __str__(self):
        tokens_str = " ".join([str(token) for token in self.tokens])
        return "{}".format(tokens_str)

    def __repr__(self):
        tokens_str = " | ".join([repr(token) for token in self.tokens])
        return "{}[{}]: {}".format(self.line_n, self.level, tokens_str)


class Block(Expression):
    def __init__(self, parent: 'Block' or None, first_line: Line):
        self.first_line = first_line
        self.parent = parent
        self.block_lines = []  # type: List[Expression]

    def push(self, smth: Line or 'Block'):
        assert isinstance(smth, Line) or isinstance(smth, Block)
        self.block_lines.append(smth)

    def pop(self) -> Line or 'Block':
        return self.block_lines.pop()

    @property
    def line_n(self) -> int:
        return self.first_line.line_n

    @property
    def tokens(self) -> List[Token]:
        return self.first_line.tokens

    @property
    def func_token(self) -> Token:
        return self.first_line.tokens[0]

    @property
    def args(self) -> List[Token]:
        return self.first_line.tokens[1:]

    @property
    def level(self) -> int:
        return self.first_line.level

    def __repr__(self):
        result = ""
        if self.first_line.level < 0:
            result += "RootBlock"
        else:
            result += "Block[{func_name}]".format(
                func_name=self.first_line.func_token.text,
            )
        result += " {lines} lines inside".format(
            lines=len(self.block_lines)
        )
        return result

    def debug_print(self, level=0, _ident=4, view_func=str):
        def ident(s):
            return " " * _ident * level + view_func(s)

        lines = []
        if self.first_line.level >= 0:
            lines.append(ident(self.first_line))
        level += 1
        for line in self.block_lines:
            if isinstance(line, Line):
                lines.append(ident(line))
            elif isinstance(line, Block):
                lines += line.debug_print(level=level, _ident=_ident)
            else:
                lines += "UNKNOWN OBJ T:`{}` V:`{}`".format(
                    type(line),
                    line
                )
        return lines


class CodeInception(Expression):
    """Используется для внедрения кода в macroblock"""

    @property
    def args(self) -> List[Token]:
        return self.expr.args

    @property
    def level(self) -> int:
        return self.expr.level

    @property
    def func_token(self) -> Token:
        return self.expr.func_token

    def __init__(self, expr: Expression, func_name: str):
        self.name = "code"
        self.func_name = func_name
        self.expr = expr
        self.line_n = expr.line_n
