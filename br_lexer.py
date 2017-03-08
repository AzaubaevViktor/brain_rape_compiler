import abc
from typing import List


class Token:
    def __init__(self, line_n: int, pos: int, text: str):
        self.line_n = line_n
        self.pos = pos
        self.text = text

    def __repr__(self):
        return "{}:{}<{}>".format(self.line_n, self.pos, self.text)

    def __str__(self):
        return "{}".format(self.text)


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
                 level: int,
                 tokens: List[Token],
                 source: str):
        self.line_n = line_n
        self._level = level
        self.tokens = tokens
        self.source = source

    @property
    def func_token(self) -> Token:
        return self.tokens[0]

    @property
    def args(self) -> List[Token]:
        return self.tokens[1:]

    @property
    def level(self) -> int:
        return self._level

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