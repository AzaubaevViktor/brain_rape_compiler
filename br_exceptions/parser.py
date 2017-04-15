from br_exceptions.base import Base as _Base


class Base(_Base):
    pass


class ArgumentCheckError(Base):
    fmt = "Неверное количество аргументов."


class ArgumentLenError(ArgumentCheckError):
    def __str__(self):
        s = "Неверное количество агрументов: `{}` вместо `{}`\n".format(
            len(self.context.expr.args),
            len(self.context.func.arguments)
        )

        s += self.context.error_info(self.token)

        return s


class ArgumentParseError(ArgumentCheckError):
    def __init__(self, type_error: 'BaseTypeError',
                 identifier_error: 'IdentifierNameError'):
        self.type_error = type_error
        self.identifier_error = identifier_error

    def __str__(self):
        s = "Ошибка разбора аргумента.\n"
        s += "Либо:\n{}\n".format(repr(self.type_error))
        s += "Либо:\n{}\n".format(repr(self.identifier_error))
        s += self.context.error_info(self.token)

        return s


class ArgumentCheckTypeError(ArgumentCheckError):
    def __init__(self, need: 'AbstractType',
                 accepted: 'AbstractBrType'
                 ):
        self.need = need
        self.accepted = accepted

    def __str__(self):
        s = "Несовместимые типы.\n"
        s += "Ожидается: `{}`\n".format(self.need.name)
        s += "Передано:  `{}`\n".format(self.accepted.name)

        s += self.context.error_info(self.token)

        return s


class SymbolDuplicate(Base):
    def __init__(self, token: 'Token'):
        self.token = token

    def __str__(self):
        s = "Дублирующийся символ {} с именем {}".format(
            self.token,
            self.token.text
        )


class SymbolNotFoundException(Base):
    _what = "символ"

    def __init__(self, token: 'Token'):
        self.token = token

    def __str__(self):
        s = "Невозможно найти {} с именем `{}`".format(
            self.__class__._what,
            self.token.text
        )
        s += "\n"
        s += self.context.error_info(self.token)
        return s


class FunctionNotFoundError(SymbolNotFoundException):
    _what = "функцию"


class VariableNotFoundError(SymbolNotFoundException):
    _what = "переменную"



class CodeInceptionError(Base):
    def __str__(self):
        s = self.__class__.__repr__(self)
        s += "\n"
        s += self.context.error_info(self.token)
        return s


class CodeInceptionArgumentsError(CodeInceptionError):
    def __repr__(self):
        return "Code Inception не может иметь аргументов"


class CodeInceptionBlockError(CodeInceptionError):
    def __repr__(self):
        return "Code Inception не может быть блоковой функцией"


class CodeInceptionNotFound(CodeInceptionError):
    def __repr__(self):
        return "Code inception for {} not found".format(
            self.token.text
        )
