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
        s += "Либо:\n{}\n".format(str(self.type_error))
        s += "Либо:\n{}\n".format(str(self.identifier_error))
        s += self.context.error_info(self.token)

        return s


class ArgumentCheckTypeError(ArgumentCheckError):
    def __str__(self):
        return "Невозможно сопоставить тип, ошибка:\n====\n" \
               "{}\n" \
               "{}".format(type(self.exc), self.exc)


class SymbolNotFoundException(Base):
    _what = "символ"

    def __init__(self, token: 'Token'):
        self.token = token

    def __str__(self):
        return "Невозможно найти {} с именем `{}`".format(
            self.__class__._what,
            self.token.text
        )


class FunctionNotFoundError(SymbolNotFoundException):
    _what = "функцию"


class VariableNotFoundError(SymbolNotFoundException):
    _what = "переменную"

    def __str__(self):
        s = super().__str__()
        s += "\n"
        s += self.context.error_info(self.token)
        return s
