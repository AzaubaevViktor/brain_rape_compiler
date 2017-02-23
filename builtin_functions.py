import sys
import traceback
from typing import Dict

from br_exceptions.parser import *
from br_lexer import Token, Expression
from br_parser import Function, Argument, FunctionLifeTime, FunctionType, NameSpace, \
    Variable
from br_types import IntBrType, IdentifierBrType, BrTypeBrType, \
    FunctionLifeTimeBrType, AddressBrType
from bytecode import ByteCode as B


class _Nope(Function):
    def compile(self,
                variables: Dict[str, Variable]
                ):
        return [
            B("#", "Nope func")
        ]

nope = _Nope(
    'nope',
    [],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Add(Function):
    def compile(self,
                variables: Dict[str, Variable],
                namespace: 'NameSpace' = None):
        addr = namespace.get_address_value(variables['addr'])
        value = variables['value'].value
        return [
            B(">", addr),
            B("+", value),
            B("<", addr)
        ]

add = _Add(
    '_add',
    [
        Argument('addr', AddressBrType),
        Argument('value', IntBrType)
    ],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Mov(Function):
    def compile(self,
                variables: Dict[str, Variable],
                namespace: 'NameSpace' = None):
        to_addr = variables['to_addr'].value
        from_addr = variables['from_addr'].value
        return [
            B(">", from_addr - 0),  # Move to from_addr
            B("[", 0),  # While *from_addr not null, do
            B("-", 1),  # *from_addr -= 1
            B(">", to_addr - from_addr),  # go to to_addr
            B("+", 1),  # *to_addr += 1
            B(">", from_addr - to_addr),  # go to from_addr
            B("]", 0),  # if *from_addr == null then end
            B(">", 0 - from_addr)  # move to 0
        ]

mov = _Mov(
    '_mov',
    [
        Argument('to_addr', AddressBrType),
        Argument('from_addr', AddressBrType)
    ],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Mov2(Function):
    def compile(self,
                variables: Dict[str, Variable],
                namespace: 'NameSpace' = None):
        to1_addr = variables['to1_addr'].value
        to2_addr = variables['to2_addr'].value
        from_addr = variables['from_addr'].value
        return [
            B(">", from_addr - 0),  # Move to from_addr
            B("["),  # While *from_addr not null, do
            B("-", 1),  # *from_addr -= 1
            B(">", to1_addr - from_addr),  # go to to1_addr
            B("+", 1),  # *to1_addr += 1
            B(">", to2_addr - to1_addr),  # goto to2_addr
            B("+", 1),  # *to2_addr += 1
            B(">", from_addr - to2_addr),  # go to from_addr
            B("]"),  # if *from_addr == null then end
            B(">", 0 - from_addr)  # move to 0
        ]

mov2 = _Mov2(
    '_mov2',
    [
        Argument('to1_addr', AddressBrType),
        Argument('to2_addr', AddressBrType),
        Argument('from_addr', AddressBrType)
    ],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Null(Function):
    def compile(self,
                variables: Dict[str, Variable],
                namespace: 'NameSpace' = None):
        addr = variables['addr'].value
        return [
            B(">", addr - 0),   # goto addr
            B("["),   # [
            B("-", 1),     # -
            B("]"),  # ]
            B(">", 0 - addr)   # goto 0
        ]

null = _Null(
    '_null',
    [
        Argument('addr', AddressBrType)
    ],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Print(Function):
    def compile(self,
                variables: Dict[str, Variable],
                namespace: 'NameSpace' = None):
        addr = variables['addr'].value
        return [
            B(">", addr - 0),    # goto addr
            B("."),           # print from addr
            B(">", 0 - addr)     # goto 0
        ]

_print = _Print(
    '_print',
    [
        Argument('addr', AddressBrType)
    ],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Read(Function):
    def compile(self,
                variables: Dict[str, Variable],
                namespace: 'NameSpace' = None):
        addr = variables['addr'].value
        return [
            B(">", addr - 0),
            B(","),
            B(">", 0 - addr)
        ]


_read = _Read(
    '_read',
    [
        Argument('addr', AddressBrType)
    ],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Main(Function):
    pass


_main = _Main(
    '__main',
    [],
    FunctionType.BLOCK,
    FunctionLifeTime.ONLY_CURRENT,
    code=([], []),  # hack for textual insert
    builtin=True
)


class _Macro(Function):
    def check_args(self, params: List[Token]) -> Dict[str, Variable]:
        variables = {}
        if len(params) < 2:
            raise ParserArgumentCheckLenException(self, params, 2)
        if len(params) % 2:
            raise ParserArgumentCheckLenException(self, params, len(params) + 1)

        params_iter = iter(params)
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
            traceback.print_exception(*sys.exc_info())
            raise ParserArgumentCheckTypeException(
                self,
                params,
                exc=e
            )

        return variables

    def compile_block(self,
                      variables: Dict[str, Variable],
                      block_inside: List[Expression] or None = None,
                      namespace: NameSpace = None
                      ):
        function_name = variables['name'].value
        arguments = variables['arguments']  # type: List[Argument]
        lifetime = variables['lifetime'].value
        # Because variables['arguments'] List[Argument], not Variable
        namespace.symbol_push(
            Function(
                function_name,
                arguments,
                FunctionType.NO_BLOCK,
                lifetime,
                source=block_inside,
                code=block_inside,
            )
        )
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

builtin_functions = [
    nope,
    add,
    mov,
    mov2,
    null,
    _print,
    _read,
    macro,
    _main
]
