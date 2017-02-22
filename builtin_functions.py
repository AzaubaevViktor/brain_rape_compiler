from br_exceptions.parser import *
from br_lexer import Token, Expression
from br_parser import Function, Argument, FunctionLifeTime, FunctionType, NameSpace
from br_types import AbstractBrType, IntBrType, IdentifierBrType, BrTypeBrType
from bytecode import ByteCode as B


class _Add(Function):
    def compile(self, variables: Dict[str, AbstractBrType]):
        addr = variables['addr'].value
        value = variables['value'].value
        return [
            B(">", addr),
            B("+", value),
            B("<", addr)
        ]

add = _Add(
    '_add',
    [
        Argument('addr', IntBrType),
        Argument('value', IntBrType)
    ],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Mov(Function):
    def compile(self, variables: Dict[str, AbstractBrType]):
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
        Argument('to_addr', IntBrType),
        Argument('from_addr', IntBrType)
    ],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Mov2(Function):
    def compile(self, variables: Dict[str, AbstractBrType]):
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
        Argument('to1_addr', IntBrType),
        Argument('to2_addr', IntBrType),
        Argument('from_addr', IntBrType)
    ],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Null(Function):
    def compile(self, variables: Dict[str, AbstractBrType]):
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
        Argument('addr', IntBrType)
    ],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Print(Function):
    def compile(self, variables: Dict[str, AbstractBrType]):
        addr = variables['addr'].value
        return [
            B(">", addr - 0),    # goto addr
            B("."),           # print from addr
            B(">", 0 - addr)     # goto 0
        ]

_print = _Print(
    '_print',
    [
        Argument('addr', IntBrType)
    ],
    FunctionType.NO_BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)


class _Read(Function):
    def compile(self, variables: Dict[str, AbstractBrType]):
        addr = variables['addr'].value
        return [
            B(">", addr - 0),
            B(","),
            B(">", 0 - addr)
        ]


_read = _Read(
    '_read',
    [
        Argument('addr', IntBrType)
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
    def check_args(self, params: List[Token]) -> Dict[str, AbstractBrType]:
        variables = {}
        if len(params) < 2:
            raise ParserArgumentCheckLenException(self, params, 2)
        if len(params) % 2:
            raise ParserArgumentCheckLenException(self, params, len(params) + 1)

        params_iter = iter(params)
        try:
            variables['lifetime'] = FunctionLifeTime(next(params_iter))
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
            raise ParserArgumentCheckTypeException(
                self,
                params,
                exc=e
            )

        return variables

    def compile_block(self,
                      variables: Dict[str, AbstractBrType],
                      block_inside: List[Expression] or None = None,
                      namespace: NameSpace = None
                      ):
        # Because variables['arguments'] List[Argument], not AbstractBrType
        # noinspection PyTypeChecker
        namespace.function_push(
            Function(
                variables['name'].value,
                variables['arguments'],
                FunctionType.NO_BLOCK,
                variables['lifetime'].value,
                source=block_inside,
                code=block_inside,
            )
        )
        return []

_macro = _Macro(
    "macro",
    [],  # because custom check_args
    FunctionType.BLOCK,
    FunctionLifeTime.GLOBAL,
    builtin=True
)

builtin_functions = [
    add,
    mov,
    mov2,
    null,
    _print,
    _read,
    _main
]
