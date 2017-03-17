from typing import Dict, List

from br_exceptions.parser import *
from br_lexer import Token, Expression
from br_parser import Function, Argument, FunctionLifeTime, FunctionType, NameSpace, \
    Variable
from br_types import IntBrType, IdentifierBrType, BrTypeBrType, \
    FunctionLifeTimeBrType, AddressBrType
from bytecode import ByteCode as B


class _Nope(Function):
    def compile(self, context: 'Context') -> List[B]:
        return [
            B("#", "Nope func")
        ]

nope = _Nope(
    '__nope',
    [],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Plus(Function):
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
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Minus(Function):
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
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _MovAbs(Function):
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
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _MovAbsL(Function):
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
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Move(Function):
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
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Print(Function):
    def compile(self, context: 'Context') -> List[B]:
        return [
            B("."),
        ]

_print = _Print(
    '__print',
    [],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Read(Function):
    def compile(self, context: 'Context') -> List[B]:
        return [
            B(","),
        ]


read = _Read(
    '__read',
    [],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _CycleStart(Function):
    def compile(self, context: 'Context'):
        return [
            B("[")
        ]

cycle_start = _CycleStart(
    "__cycle_start",
    [],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _CycleEnd(Function):
    def compile(self, context: 'Context'):
        return [
            B("]")
        ]

cycle_end = _CycleEnd(
    "__cycle_end",
    [],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Macro(Function):
    def check_args(self, context: 'Context') -> Dict[str, Variable]:
        arg_tokens = context.expr.args
        variables = {}
        if len(arg_tokens) < 2:
            raise ArgumentLenError(self, arg_tokens, 2)
        if len(arg_tokens) % 2:
            raise ArgumentLenError(self, arg_tokens, len(arg_tokens) + 1)

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
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _MacroBlock(_Macro):
    def compile_block(self, context: 'Context') -> List[B]:
        function_name = context.vars['name'].value
        arguments = context.vars['arguments']  # type: List[Argument]
        lifetime = context.vars['lifetime'].value

        code = [[]]

        block_inside = context.expr.block_lines

        # OH SHIT
        # Не работает code, если её вставлять в другую вложенность

        for expr in block_inside:  # type: Expression
            if str(expr.func_token) == 'code':
                code.append([])
            else:
                code[-1].append(expr)

        func = Function(
            function_name,
            arguments,
            FunctionType.BLOCK,
            lifetime,
            source=block_inside,
            code=code,
        )

        context.ns.symbol_lifetime_push(lifetime, func)

        return [
            B(B.NONE,
              "Add macro function `{}` to current namespace".format(function_name)
              ),
        ]


macroblock = _MacroBlock(
    "macroblock",
    [],  # because custom check_args
    FunctionType.BLOCK,
    FunctionLifeTime.GLOBAL,
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
    FunctionLifeTime.GLOBAL,
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
    macroblock
]
