import abc
from typing import List, Iterator

import br_lexer.excs as lex_exc
from .token import Token


class Expression(metaclass=abc.ABCMeta):
    @property
    def level(self):
        return self._level

    @property
    def parent(self):
        return self._parent

    @property
    def number(self):
        return self._number

    @property
    @abc.abstractmethod
    def func_token(self) -> Token:
        pass

    @property
    @abc.abstractmethod
    def argument_tokens(self) -> List[Token]:
        pass

    @abc.abstractmethod
    def debug_print(self, ident: int = 4) -> str:
        pass


class Line(Expression):
    def __init__(self, stream: 'Stream', number: int, text: str):
        self.stream = stream
        self.text = text.rstrip()

        self._number = number
        self._parent = None
        self._level = self._calc_level()
        self.tokens = self._calc_tokens()

        self.next_line = None  # type: Line or None
        self.prev_line = None  # type: Line or None

    def _calc_level(self):
        level = 0
        for ch in self.text:
            if " " == ch:
                level += 1
            else:
                break

        if level % 4:
            raise lex_exc.LevelError(self,
                                     None,
                                     under_start=0,
                                     under_len=level
                                     )

        return level // 4

    def _calc_tokens(self) -> List[Token]:
        tokens = []
        pos = 0
        for word in self.text.split(" "):
            if len(word.strip()):
                # Комментарии отсекаем
                if '#' == word[0]:
                    break
                tokens.append(Token(self, pos, word.strip()))
                pos += len(word)

            pos += 1

        return tokens

    @property
    def func_token(self) -> Token:
        return self.tokens[0]

    @property
    def argument_tokens(self) -> List[Token]:
        return self.tokens[1:]

    def __bool__(self):
        return 0 != len(list(self.tokens))

    def __repr__(self):
        return "Line<{}: `{}`>".format(
            self.number,
            " ".join([repr(t) for t in self.tokens])
        )

    def debug_print(self, ident: int = 4) -> str:
        s = "{}: {}{}({})".format(
            self.number,
            " " * ident * self.level,
            self.func_token.text,
            ", ".join(t.text for t in self.argument_tokens)
        )
        return s


class Block(Expression):
    def __init__(self, head_line: Line, content: List[Expression] = None):
        self.head_line = head_line
        self.content = content or []  # type: List[Expression]

        self._number = self.head_line.number
        self._level = self.head_line.level
        self._parent = None

    def push(self, expr: Expression):
        self.content.append(expr)
        expr._parent = self

    def pop(self) -> Expression:
        expr = self.content.pop()
        expr._parent = None
        return expr

    @property
    def func_token(self) -> Token:
        return self.head_line.func_token

    @property
    def argument_tokens(self) -> List[Token]:
        return self.head_line.argument_tokens

    def debug_print(self, ident: int = 4) -> str:
        s = self.head_line.debug_print(ident) + "\n"

        for expr in self.content:
            s += expr.debug_print(ident) + "\n"

        return s[:-1]
