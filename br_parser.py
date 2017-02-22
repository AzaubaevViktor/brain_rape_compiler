import typing
from enum import Enum
from typing import List, Dict, Type, TypeVar, Tuple

from br_exceptions.parser import ParserArgumentCheckLenException, ParserArgumentCheckTypeException, \
    ParserFunctionNotFoundException
from br_lexer import Line, Token, Block
from br_types import AbstractBrType
from bytecode import ByteCode


class Argument:
    def __init__(self, name: str, _type: Type[AbstractBrType]):
        self.name = name
        self.type = _type

    def apply(self, token: Token) -> AbstractBrType:
        return self.type(token)


class BrFunctionType(Enum):
    NO_BLOCK = 1
    BLOCK = 2


class BrFunctionLifeTime(Enum):
    GLOBAL = 1  # Текущий namespace и дочерние
    ONLY_CURRENT = 2  # Только этот namespace (Для __main)


class BrFunction:
    def __init__(self,
                 name: str,
                 arguments: List[Argument],
                 _type: BrFunctionType,
                 lifetime: BrFunctionLifeTime,
                 source: List[Line] or None = None,
                 code: List[Line or Block] or Tuple(List[Line or Block], List[Line or Block]) or None = None,
                 builtin: bool = False
                 ):
        self.name = name
        self.arguments = arguments
        self.type = _type
        self.lifetime = lifetime
        self.source = source
        self.code = code
        self.builtin = builtin

    def check_args(self, params: List[Token]) -> Dict[str, AbstractBrType]:
        variables = {}
        if len(self.arguments) != len(params):
            raise ParserArgumentCheckLenException(
                self,
                params
            )
        try:
            for arg, var in zip(self.arguments, params):
                variables[arg.name] = arg.apply(var)
        except Exception as e:
            raise ParserArgumentCheckTypeException(
                self,
                params,
                exc=e
            )
        return variables

    def compile(self,
                variables: Dict[str, AbstractBrType]
                ) -> List[ByteCode]:
        raise NotImplemented()

    def compile_block(self,
                      variables: Dict[str, AbstractBrType],
                      block_inside: List[Line or Block] or None = None,
                      namespace: 'NameSpace' = None
                      ) -> List[ByteCode]:
        raise NotImplemented()


class NameSpace:
    def __init__(self, parent: 'NameSpace' or None):
        self.parent = parent  # type: NameSpace
        self.functions = {}

    def function_push(self, func: BrFunction):
        self.functions[func.name] = func

    def functions_push(self, funcs: List[BrFunction]):
        for func in funcs:
            self.function_push(func)

    def get_func_by_token(self, token: Token) -> BrFunction:
        func_name = token.text
        if func_name in self.functions:
            return self.functions[func_name]
        elif self.parent:
            return self.parent.get_func_by_token(token)
        else:
            raise ParserFunctionNotFoundException(token)

    def create_namespace(self):
        ns = NameSpace(self)
        return ns

