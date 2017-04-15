from typing import Dict, List

from br_exceptions import parser as parser_e
from br_lexer import Expression, Block, CodeInception
from br_parser import Function, Argument, LifeTime, FunctionType, NameSpace, \
    Variable
from br_types import IntBrType, IdentifierBrType, BrTypeBrType, \
    FunctionLifeTimeBrType, AddressBrType, StrBrType
from bytecode import ByteCode as B


class _Nope(Function):
    """ Функция ничего не делает """
    def compile(self, context: 'Context') -> List[B]:
        return [
            B("#", "Nope func")
        ]

nope = _Nope(
    '__nope',
    [],
    FunctionType.NO_BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


class _Plus(Function):
    """ Стандартный `+` из BF """
    def compile(self, context: 'Context') -> List[B]:
        value = context.vars['value'].value
        return [
            B("+", value),
        ]

plus = _Plus(
    '__plus',
    [
        Argument('value', IntBrType)
    ],
    FunctionType.NO_BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


class _Minus(Function):
    """ Стандартный `-` из BF """
    def compile(self, context: 'Context') -> List[B]:
        value = context.vars['value'].value
        return [
            B("-", value),
        ]

minus = _Minus(
    '__minus',
    [
        Argument('value', IntBrType)
    ],
    FunctionType.NO_BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


class _MovAbs(Function):
    """ `>` """
    def compile(self, context: 'Context') -> List[B]:
        value = context.vars['value'].value
        return [
            B(">", value),
        ]

mov_abs = _MovAbs(
    '__movabs',
    [
        Argument('value', IntBrType)
    ],
    FunctionType.NO_BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


class _MovAbsL(Function):
    """ `<` """
    def compile(self, context: 'Context') -> List[B]:
        value = context.vars['value'].value
        return [
            B("<", value),
        ]

mov_abs_l = _MovAbsL(
    '__movabsl',
    [
        Argument('value', IntBrType)
    ],
    FunctionType.NO_BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


class _Move(Function):
    """ Переместить с адреса from на адрес to """
    def compile(self, context: 'Context') -> List[B]:
        addr_to = context.vars['to'].value
        addr_from = context.vars['from'].value
        return [
            B(">", addr_to - addr_from),
        ]

move = _Move(
    '__move',
    [
        Argument('to', AddressBrType),
        Argument('from', AddressBrType),
    ],
    FunctionType.NO_BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


class _Print(Function):
    """ Распечатать текущую ячейку """
    def compile(self, context: 'Context') -> List[B]:
        return [
            B("."),
        ]

_print = _Print(
    '__print',
    [],
    FunctionType.NO_BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


class _Read(Function):
    """ Считать в текущую ячейку """
    def compile(self, context: 'Context') -> List[B]:
        return [
            B(","),
        ]


read = _Read(
    '__read',
    [],
    FunctionType.NO_BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


class _CycleStart(Function):
    """ Начало цикла """
    def compile(self, context: 'Context'):
        return [
            B("[")
        ]

cycle_start = _CycleStart(
    "__cycle_start",
    [],
    FunctionType.NO_BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


class _CycleEnd(Function):
    """ Конец цикла """
    def compile(self, context: 'Context'):
        return [
            B("]")
        ]

cycle_end = _CycleEnd(
    "__cycle_end",
    [],
    FunctionType.NO_BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


class _Macro(Function):
    def check_args(self, context: 'Context') -> Dict[str, Variable]:
        arg_tokens = context.expr.args
        variables = {}
        # TODO: Исправить проверку на более понятную
        if len(arg_tokens) < 2:
            raise parser_e.ArgumentLenError(context, arg_tokens[2])
        if len(arg_tokens) % 2:
            raise parser_e.ArgumentLenError(context, arg_tokens[len(arg_tokens) - 1])

        params_iter = iter(arg_tokens)
        try:
            variables['lifetime'] = FunctionLifeTimeBrType(next(params_iter))
            variables['name'] = IdentifierBrType(next(params_iter))
            variables['arguments'] = []

            try:
                while True:
                    arg_type = BrTypeBrType(next(params_iter)).value
                    arg_name = IdentifierBrType(next(params_iter)).value
                    variables['arguments'].append(
                        Argument(arg_name, arg_type)
                    )

            except StopIteration:
                pass
        except Exception as e:
            e.context = context
            raise e

        return variables

    def compile_block(self, context: 'Context') -> List[B]:
        function_name = context.vars['name'].value
        arguments = context.vars['arguments']  # type: List[Argument]
        lifetime = context.vars['lifetime'].value
        # Because variables['arguments'] List[Argument], not Variable

        block_inside = context.expr.block_lines
        func = Function(
            function_name,
            arguments,
            FunctionType.NO_BLOCK,
            lifetime,
            source=block_inside,
            code=block_inside,
        )

        context.ns.symbol_lifetime_push(lifetime, func)

        return [
            B(B.NONE,
              "Add function `{}` to current namespace".format(function_name)
              ),
        ]

macro = _Macro(
    "macro",
    [],  # because custom check_args
    FunctionType.BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


class _MacroBlock(_Macro):
    def compile_block(self, context: 'Context') -> List[B]:
        function_name = context.vars['name'].value
        arguments = context.vars['arguments']  # type: List[Argument]
        lifetime = context.vars['lifetime'].value

        block_lines = context.expr.block_lines

        self.find_code_insception(
            function_name,
            block_lines
        )

        func = Function(
            function_name,
            arguments,
            FunctionType.BLOCK,
            lifetime,
            source=block_lines,
            code=block_lines,
        )

        context.ns.symbol_lifetime_push(lifetime, func)

        return [
            B(B.NONE,
              "Add macro function `{}` to current namespace".format(function_name)
              ),
        ]

    def find_code_insception(self,
                             func_name: str,
                             block_line: List[Expression]
                             ):
        for i, expr in enumerate(block_line):
            if str(expr.func_token) == 'code':
                # We found code inception directive!
                # test correct
                if len(expr.args) > 0:
                    raise parser_e.CodeInceptionArgumentsError(
                        token=expr.args[0]
                    )
                if isinstance(expr, Block):
                    raise parser_e.CodeInceptionBlockError(
                        token=expr.block_lines[0].func_token
                    )
                # ok, code inception correct
                # replace
                block_line.pop(i)
                block_line.insert(
                    i,
                    CodeInception(expr=expr,
                                  func_name=func_name)
                )
            elif isinstance(expr, Block):
                # expression is block, recursive call
                self.find_code_insception(
                    func_name,
                    expr.block_lines
                )


macroblock = _MacroBlock(
    "macroblock",
    [],  # because custom check_args
    FunctionType.BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


def _get_first_empty(busy: list) -> int:
    busy = sorted(busy)
    for i, v in zip(range(len(busy)), busy):
        if i != v:
            return i
    return len(busy)


class _Reg(Function):
    def compile(self, context: 'Context') -> List[B]:
        register_name = context.vars['name'].value
        busy = set()
        vars = context.ch_ns.get_vars()
        for var in vars:
            if isinstance(var.value_type, AddressBrType):
                busy.add(var.value)
        empty = _get_first_empty(sorted(list(busy)))
        context.ns.symbol_push(
            Variable(register_name, AddressBrType(None, value=empty))
        )
        return [
            B("#",
              "Added new variable `{}` "
              "with address `{}` to local namespace".format(
                  register_name,
                  empty
              )
              )
        ]


reg = _Reg(
    'reg',
    [
        Argument('name', IdentifierBrType)
    ],
    FunctionType.NO_BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)


class Import(Function):
    def compile(self, context: 'Context') -> List[B]:
        file_name = context.vars['file_name'].value
        from br_compiler import Lexer

        block = None
        with open(file_name, 'rt') as f:
            l = Lexer(file_name, f.readlines())
            block = l.block

        from br_compiler import FileCompiler
        compiler = FileCompiler(file_name, block, context)
        compiler.compile()
        return [
            B("#",
              "Imported code from `{}`".format(
                  file_name
              )
              )
        ]


_import = Import(
    'import',
    [
        Argument('file_name', StrBrType)
    ],
    FunctionType.NO_BLOCK,
    LifeTime.GLOBAL,
    builtin=True
)

builtin_functions = [
    nope,
    plus,
    minus,
    mov_abs,
    mov_abs_l,
    move,
    _print,
    read,
    cycle_start,
    cycle_end,
    macro,
    reg,
    macroblock,
    _import
]
