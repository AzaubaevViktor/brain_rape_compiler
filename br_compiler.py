from typing import Dict
from typing import Iterator
from typing import List, Tuple

from br_lexer import Block, Expression, CodeInception
from br_parser import Function, Argument, Token, Line, NameSpace, FunctionType,\
Variable
from br_exceptions import lexer as lexer_e
from br_exceptions import compiler as compiler_e
from builtin_functions import builtin_functions
from builtin_variables import builtin_variables
from bytecode import ByteCode


class Lexer:
    def __init__(self, source_lines):
        self.source_lines = source_lines
        self.lines = []  # type: List[Line]
        self.block = None  # type: Block

        self._lines_process()
        self._block_process()

    def _lines_process(self):
        """ Заполняет self.lines из файла """
        # self.file = open(self.file_name, "rt")
        line_n = 1
        for raw_line in self.source_lines:
            line = Line(line_n, raw_line)
            if line:
                self.lines.append(line)

            line_n += 1
        # self.file.close()
        # add last line for _block_process
        self.lines.append(
            Line(line_n, "nope")
        )

    def _block_process(self):
        """ Обрабатывает self.lines и где надо преобразовывает их в блоки"""
        cur_block = self.block = Block(None, Line(-1, "__main"))
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
                raise lexer_e.BlockLevelError(cur_line, next_line)


class Context:
    def __init__(self, parent: 'Context' or None,
                 expr: Expression,
                 namespace: NameSpace or None = None
                 ):
        self.parent = parent
        self.childs = []  # type: List[Context]
        self.expr = expr  # type: Expression
        self.func = None  # type: Function
        self.vars = {}  # type: Dict[str, Variable]
        # NameSpace здесь создаётся именно для ПОТОМКОВ, NameSpace, в контексте
        # оторого выполняется данное выражение находится на уровень выше
        # Предназначен только для ДОБАВЛЕНИЯ В НЕГО НОВЫХ ПЕРЕМЕННЫХ
        # предназначен для БЛОКОВЫХ ФУНКЦИЙ, ПЕРЕДАЁТСЯ В НЕГО
        self.ch_ns = namespace or NameSpace()
        self.bytecode = []  # type: List[ByteCode]

    @property
    def ns(self):
        return self.ch_ns.parent

    def create_child(self, expr: Expression) -> 'Context':
        cntx = Context(parent=self,
                       expr=expr,
                       namespace=self.ch_ns.create_namespace()
                       )
        self.childs.append(cntx)
        return cntx

    def _determine_function(self):
        if not isinstance(self.expr, CodeInception):
            self.func = self.ns.get_func(self.expr.func_token)

    def compile(self):
        # found function
        self._determine_function()
        if isinstance(self.expr, Line):
            if self.func.builtin:
                # Builtin, NoBlock
                self.vars = self.func.check_args(self)
                self.bytecode = self.func.compile(self)
            else:
                # No builtin, NoBlock
                if FunctionType.NO_BLOCK != self.func.type:
                    raise compiler_e.BlockFunctionError(
                        context=self, function=self.func)
                self.vars = self.func.check_args(self)
                self.ch_ns.symbols_push(self.vars.values())

                for expr in self.func.code:
                    cntx = self.create_child(expr)
                    cntx.compile()

        elif isinstance(self.expr, Block):
            if self.func.builtin:
                # Builtin, Block
                self.vars = self.func.check_args(self)
                self.bytecode = self.func.compile_block(self)
            else:
                # not builtin block
                if FunctionType.BLOCK != self.func.type:
                    raise compiler_e.NoBlockFunctionError(
                        context=self, function=self.func)
                self.vars = self.func.check_args(self)

                # add code inception
                self.ch_ns.add_code_inception(
                    self.func.name,
                    self.expr.block_lines
                )

                self.ch_ns.symbols_push(self.vars.values())

                for expr in self.func.code:
                    cntx = self.create_child(expr)
                    cntx.compile()
        elif isinstance(self.expr, CodeInception):
            wrapper_cntx = self.create_child(self.expr)
            block_lines = self.ns.get_code_inception(self.expr.func_name)
            for expr in block_lines:
                cntx = wrapper_cntx.create_child(expr)
                cntx.compile()

    def __str__(self):
        btcode = " ".join([str(b) for b in self.bytecode])
        btcode = btcode + "\n" if btcode else btcode
        vars = []
        if self.func:
            for arg in self.func.arguments:
                vars.append(self.vars[arg.name])

        return "{self.func}\n{vars}\n{btcode}".format(
            self=self,
            vars=vars,
            btcode=btcode or "--->"
        )

    def debug_print(self, level: int =0, view_func=str) -> List[str]:
        def ident(s):
            rs = view_func(s)
            lines = []
            for line in rs.split("\n"):
                lines.append(" " * level * 4 + line)
            return lines

        lines = []

        lines += ident(view_func(self))

        for cntx in self.childs:
            lines += cntx.debug_print(level + 1)

        return lines

    def error_info(self, token=None):
        s = " === COMPILER STACK TRACE ===\n"
        _trace = []
        cur_cntx = self
        while cur_cntx.parent:
            _trace = ["  " + _el for _el in _trace]
            _vars = ["{var.name} => {var.value_type}".format(var=var) for var in
                     cur_cntx.vars.values()]
            _trace = \
                [str(cur_cntx.func)] \
                + _vars \
                + _trace
            cur_cntx = cur_cntx.parent
        s += "\n".join(_trace) + "\n"

        s += " === LINE ===\n"

        expr = self.expr
        line_n = "{}: ".format(self.expr.line_n)
        level_tab = "   •" * expr.level
        sourcer = " ".join([t.text for t in expr.tokens])
        s += "{line_n}`{level_tab}{sourcer}`".format(
            line_n=line_n,
            level_tab=level_tab,
            sourcer=sourcer
        )
        s += "\n"
        s += " " * (len(line_n) + len(level_tab) + 1)
        for t in expr.tokens:
            s += ("^" if t == token else " ") * len(t)
            s += " "

        return s

    def full_bytecode(self):
        bytecode = self.bytecode[:]
        for cntx in self.childs:
            bytecode += cntx.full_bytecode()
        return bytecode


class FileCompiler:
    def __init__(self, file_name: str, block: Block):
        self.file_name = file_name
        self.block = block
        self.context = None  # type: Context or None
        self._init_context()

    def _init_context(self):
        """ Создаёт первичный Context"""
        context = Context(None, self.block)
        context.ch_ns.symbols_push(builtin_functions)
        context.ch_ns.symbols_push(builtin_variables)
        self.context = context

    def compile(self):
        self._init_context()
        for expr in self.block.block_lines:
            cntx = self.context.create_child(expr)
            cntx.compile()
