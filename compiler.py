from typing import List, Tuple

from br_parser import Token, Line, NameSpace
from br_exceptions.lexer import LexerLevelErrorException
from builtin_functions import builtin_add_function
from bytecode import ByteCode


class BfCompiler:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file = None
        self.lines = []
        self._lines_process()
        self.namespaces = []  # type: List[NameSpace]
        self._create_default_namespace()

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

    def _create_default_namespace(self):
        ns = NameSpace(None)
        ns.function_push(builtin_add_function)
        self.namespaces.append(ns)

    def compile(self) -> List[Tuple[List[ByteCode], Line]]:
        bytecode = []
        for line in self.lines:
            ns = self.namespaces[-1]
            func = ns.get_func_by_token(line.func_token)
            if func.builtin:
                variables = func.check_args(line.params)
                code = func.compile(variables)
                bytecode.append((code, line))
        return bytecode


if __name__ == "__main__":
    compiler = BfCompiler('test_add.br')
    print("==== LINES: ====")
    for line in compiler.lines:
        print(line)

    bytecode = compiler.compile()
    print()
    print("==== BYTECODE: ====")
    for code, line in bytecode:
        for act in code:
            print(act, end=" ")
        print()
        print(line)
        print("------")

