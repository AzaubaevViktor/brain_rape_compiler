from typing import List

from br import Token, Line
from br_exceptions.lexer import LexerLevelErrorException


class BfCompiler:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file = None
        self.lines = []
        self._lines_process()

    @staticmethod
    def _get_line_level(s):
        level = 0
        for ch in s:
            if ' ' == ch:
                level += 1
            else:
                break
        if level % 4:
            raise LexerLevelErrorException(s, level)
        return level // 4

    def _get_tokens(self, line_n: int, s: str) -> List[Token]:
        pos = 0
        tokens = []
        for word in s.split(" "):
            if len(word.strip()):
                # Комментарии отсекаем
                if '#' == word[0]:
                    break
                tokens.append(Token(line_n, pos, word.strip()))
                pos += len(word)

            pos += 1
        return tokens

    def _get_line(self, line_n: int, s: str) -> Line or None:
        level = self._get_line_level(s)
        tokens = self._get_tokens(line_n, s)
        line = None
        if tokens:
            line = Line(
                line_n,
                level,
                tokens,
                s
            )
        return line

    def _lines_process(self):
        self.file = open(self.file_name, "rt")
        line_n = 1
        for raw_line in self.file.readlines():
            line = self._get_line(line_n, raw_line)
            if line:
                self.lines.append(line)

            line_n += 1
        self.file.close()


if __name__ == "__main__":
    compiler = BfCompiler('test.br')
    for line in compiler.lines:
        print(line)




