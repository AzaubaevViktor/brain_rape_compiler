from typing import List


class Token:
    def __init__(self, line_n: int, pos: int, text: str):
        self.line_n = line_n
        self.pos = pos
        self.text = text

    def __str__(self):
        return "{}:{}<{}>".format(self.line_n, self.pos, self.text)


class Line:
    def __init__(self, line_n: int, level: int, tokens: List[Token], source: str):
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
    def __init__(self, parent: 'Block' or None, first_line: Line):
        self.first_line = first_line
        self.parent = parent
        self.block_lines = []  # type: List[Line or Block]

    def push(self, smth: Line or 'Block'):
        assert isinstance(smth, Line) or isinstance(smth, Block)
        self.block_lines.append(smth)

    def pop(self) -> Line or 'Block':
        return self.block_lines.pop()

    @property
    def func_token(self) -> Token:
        return self.first_line.tokens[0]

    @property
    def params(self) -> List[Token]:
        return self.first_line.tokens[1:]

    @property
    def level(self) -> int:
        return self.first_line.level

    def __str__(self):
        if self.first_line.level < 0:
            return "RootBlock"
        else:
            return "Block[{func_name}] {lines} inside".format(
                func_name=self.first_line.func_token.text,
                lines=len(self.block_lines)
            )

    def debug_print(self, level=0, _ident=4):
        def ident(s):
            return " " * _ident * level + str(s)

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