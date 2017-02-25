from typing import Iterator
from typing import List, Tuple

from br_lexer import Block, Expression
from br_parser import Token, Line, NameSpace, FunctionType
from br_exceptions.lexer import LexerLevelErrorException, LexerBlockLevelErrorException
from builtin_functions import builtin_functions
from builtin_variables import builtin_variables
from bytecode import ByteCode


class BrCompiler:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file = None
        self.lines = []  # type: List[Line]
        self.block = None  # type: Block
        self._lines_process()
        self._block_process()
        self.namespace = None  # type: NameSpace or None
        self._init_default_namespace()

    @staticmethod
    def _get_line_level(s):
        """ Возвращает уровень вложенности строки """
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
        """ Возвращает список токенов из строки """
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
        """ Возвращает Line из строки """
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
        """ Заполняет self.lines из файла """
        self.file = open(self.file_name, "rt")
        line_n = 1
        for raw_line in self.file.readlines():
            line = self._get_line(line_n, raw_line)
            if line:
                self.lines.append(line)

            line_n += 1
        self.file.close()
        # add last line for _block_process
        self.lines.append(
            self._get_line(line_n, "nope")
        )

    def _block_process(self):
        """ Обрабатывает self.lines и где надо преобразовывает их в блоки"""
        cur_block = self.block = Block(None, Line(-1, -1, [Token(-1, -1, "__main")], "__main"))
        cur_iter = iter(self.lines)  # type: Iterator[Line]
        next_iter = iter(self.lines)  # type: Iterator[Line]
        next(next_iter)
        for (cur_line, next_line) in zip(cur_iter, next_iter):  # type: Line
            nl = next_line.level
            cl = cur_line.level
            if cl == nl:
                # level eq
                cur_block.push(cur_line)
            elif cl + 1 == nl:
                # level up
                child_block = Block(cur_block, cur_line)
                cur_block.push(child_block)
                cur_block = child_block
            elif cl > nl:
                # level down
                cur_block.push(cur_line)
                for i in range(cl - nl):
                    cur_block = cur_block.parent
            elif cl + 1 < nl:
                # level up more then 2
                raise LexerBlockLevelErrorException(cur_line, next_line)

    def _init_default_namespace(self):
        """ Создаёт первичный NameSpace"""
        ns = NameSpace(None)
        ns.symbols_push(builtin_functions)
        ns.symbols_push(builtin_variables)
        self.namespace = ns

    def old_line_compile(self) -> List[Tuple[List[ByteCode], Line]]:
        """ Старая версия итоговой компиляции для одного уровня вложенности """
        bytecode = []
        for line in self.lines:
            ns = self.namespace[-1]
            func = ns.get_func_by_token(line.func_token)
            if func.builtin:
                #  Builtin NoBlock function
                if FunctionType.NO_BLOCK == func.type:
                    variables = func.check_args(line.params)
                    code = func.compile(variables)
                    bytecode.append((code, line))
                #  Builtin Block Function
                elif FunctionType.BLOCK == func.type:
                    pass
            else:
                pass
        return bytecode

    def compile(self):
        self._init_default_namespace()
        return self._compile(
            self.namespace,
            self.block.block_lines
        )

    def _compile(self,
                 namespace: NameSpace,
                 expressions: List[Expression]
                 ) -> List[Tuple[List[ByteCode], Expression]]:
        bytecode = []
        for expr in expressions:
            func = namespace.get_func(expr.func_token)
            if isinstance(expr, Line):
                if func.builtin:
                    # Builtin no block
                    variables = func.check_args(expr.params, namespace)
                    code = func.compile(variables, namespace)
                    bytecode.append((code, func, expr))
                else:
                    # not builtin no block
                    variables = func.check_args(expr.params, namespace)
                    code = func.code
                    new_ns = namespace.create_namespace()
                    new_ns.symbols_push(variables.values())
                    bytecode += self._compile(new_ns, code)

            elif isinstance(expr, Block):
                if func.builtin:
                    # builtin block
                    variables = func.check_args(expr.params)
                    code = func.compile_block(
                        variables,
                        expr.block_lines,
                        namespace
                    )
                    bytecode.append((code, func, expr))
                    pass
                else:
                    # not builtin block
                    pass

        return bytecode

        # func: not builtin and block
        #   new namespace
        #   recursive compile:
        #       params
        #       block.code[0] + block_inside + block.code[1]
        # func: not builtin and not block
        #   recursive compile:
        #       params
        #       block_inside
        # func: builtin and block
        #   func.block_compile
        #   if not:
        #       not builtin + block compile
        # func: builtin and not block
        #    func.compile
        pass
