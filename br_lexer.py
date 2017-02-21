from typing import List


class Token:
    def __init__(self, line_n: int, pos: int, text: str):
        self.line_n = line_n
        self.pos = pos
        self.text = text

    def __str__(self):
        return "{}:{}<{}>".format(self.line_n, self.pos, self.text)


class Line:
    def __init__(self, line_n: int,  level: int, tokens: List[Token], source: str):
        self.line_n = line_n
        self.level = level
        self.tokens = tokens
        self.source = source

    @property
    def func_token(self) -> Token:
        return self.tokens[0]

    @property
    def params(self) -> List[Token]:
        return self.tokens[1:]

    def __str__(self):
        tokens_str = " | ".join([str(token) for token in self.tokens])
        return "{}[{}]: {}".format(self.line_n, self.level, tokens_str)


class Block:
    def __init__(self):
        pass