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


class ArgumentCheckTypeError(ArgumentCheckError):
    def __str__(self):

        return "Невозможно сопоставить тип, ошибка:\n====\n" \
               "{}\n" \
               "{}".format(type(self.exc), self.exc)


class ParserArgumentTypeEqException(Base):
    def __init__(self,
                 type1: 'BrType',
                 type2: 'BrType'
                 ):
        self.type1 = type1
        self.type2 = type2

    def __str__(self):
        return "Несовместимые типы. " \
               "Ожидается {}, " \
               "передано {}".format(
            self.type1,
            self.type2
        )


class ParserSymbolNotFoundException(Base):
    _what = "символ"

    def __init__(self, token: 'Token'):
        self.token = token

    def __str__(self):
        return "Невозможно найти {} с именем `{}`".format(
            self._what,
            self.token.text
        )


class ParserFunctionNotFoundException(ParserSymbolNotFoundException):
    _what = "функцию"


class ParserVariableNotFoundException(ParserSymbolNotFoundException):
    _what = "переменную"
