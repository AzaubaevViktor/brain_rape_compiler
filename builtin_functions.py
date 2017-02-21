from br_exceptions.parser import *
from br_lexer import Line, Token, Block
from br_parser import BrFunction, Argument, BrFunctionLifeTime, BrFunctionType, NameSpace
from br_types import AbstractBrType, IntBrType, IdentifierBrType, BrTypeBrType
from bytecode import ByteCode as B


class _Add(BrFunction):
    def compile(self, variables: Dict[str, AbstractBrType]):
        addr = variables['addr'].value
        value = variables['value'].value
        return [
            B(B.MOVE, addr),
            B(B.PLUS, value),
            B(B.MOVE, -addr)
        ]

add = _Add(
    '_add',
    [
        Argument('addr', IntBrType),
        Argument('value', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    builtin=True
)


class _Mov(BrFunction):
    def compile(self, variables: Dict[str, AbstractBrType]):
        to_addr = variables['to_addr'].value
        from_addr = variables['from_addr'].value
        return [
            B(B.MOVE, from_addr - 0),  # Move to from_addr
            B(B.CYCLE_IN, 0),  # While *from_addr not null, do
            B(B.PLUS, -1),  # *from_addr -= 1
            B(B.MOVE, to_addr - from_addr),  # go to to_addr
            B(B.PLUS, 1),  # *to_addr += 1
            B(B.MOVE, from_addr - to_addr),  # go to from_addr
            B(B.CYCLE_OUT, 0),  # if *from_addr == null then end
            B(B.MOVE, 0 - from_addr)  # move to 0
        ]

mov = _Mov(
    '_mov',
    [
        Argument('to_addr', IntBrType),
        Argument('from_addr', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    builtin=True
)


class _Mov2(BrFunction):
    def compile(self, variables: Dict[str, AbstractBrType]):
        to1_addr = variables['to1_addr'].value
        to2_addr = variables['to2_addr'].value
        from_addr = variables['from_addr'].value
        return [
            B(B.MOVE, from_addr - 0),  # Move to from_addr
            B(B.CYCLE_IN),  # While *from_addr not null, do
            B(B.PLUS, -1),  # *from_addr -= 1
            B(B.MOVE, to1_addr - from_addr),  # go to to1_addr
            B(B.PLUS, 1),  # *to1_addr += 1
            B(B.MOVE, to2_addr - to1_addr),  # goto to2_addr
            B(B.PLUS, 1),  # *to2_addr += 1
            B(B.MOVE, from_addr - to2_addr),  # go to from_addr
            B(B.CYCLE_OUT),  # if *from_addr == null then end
            B(B.MOVE, 0 - from_addr)  # move to 0
        ]

mov2 = _Mov2(
    '_mov2',
    [
        Argument('to1_addr', IntBrType),
        Argument('to2_addr', IntBrType),
        Argument('from_addr', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    builtin=True
)


class _Null(BrFunction):
    def compile(self, variables: Dict[str, AbstractBrType]):
        addr = variables['addr'].value
        return [
            B(B.MOVE, addr - 0),   # goto addr
            B(B.CYCLE_IN),   # [
            B(B.PLUS, -1),     # -
            B(B.CYCLE_OUT),  # ]
            B(B.MOVE, 0 - addr)   # goto 0
        ]

null = _Null(
    '_null',
    [
        Argument('addr', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    builtin=True
)


class _Print(BrFunction):
    def compile(self, variables: Dict[str, AbstractBrType]):
        addr = variables['addr'].value
        return [
            B(B.MOVE, addr - 0),    # goto addr
            B(B.PRINT),           # print from addr
            B(B.MOVE, 0 - addr)     # goto 0
        ]

_print = _Print(
    '_print',
    [
        Argument('addr', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    builtin=True
)


class _Read(BrFunction):
    def compile(self, variables: Dict[str, AbstractBrType]):
        addr = variables['addr'].value
        return [
            B(B.MOVE, addr - 0),
            B(B.READ),
            B(B.MOVE, 0 - addr)
        ]


_read = _Read(
    '_read',
    [
        Argument('addr', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    builtin=True
)


class _Main(BrFunction):
    pass


_main = _Main(
    '__main',
    [],
    BrFunctionType.BLOCK,
    BrFunctionLifeTime.ONLY_CURRENT,
    code=([], []),  # hack for textual insert
    builtin=True
)


class _Macro(BrFunction):
    def check_args(self, params: List[Token]) -> Dict[str, AbstractBrType]:
        variables = {}
        if len(params) < 2:
            raise ParserArgumentCheckLenException(self, params, 2)
        if len(params) % 2:
            raise ParserArgumentCheckLenException(self, params, len(params) + 1)

        params_iter = iter(params)
        try:
            variables['lifetime'] = BrFunctionLifeTime(next(params_iter))
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
                      block_inside: List[Line or Block] or None = None,
                      namespace: NameSpace = None
                      ):
        # Because variables['arguments'] List[Argument], not AbstractBrType
        # noinspection PyTypeChecker
        namespace.function_push(
            BrFunction(
                variables['name'].value,
                variables['arguments'],
                BrFunctionType.NO_BLOCK,
                variables['lifetime'].value,
                source=block_inside,
                code=block_inside,
            )
        )
        return []

_macro = _Macro(
    "macro",
    [],  # because custom check_args
    BrFunctionType.BLOCK,
    BrFunctionLifeTime.GLOBAL,
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
