from br_exceptions.base import Base


class BaseTypesError(Base):
    def __init__(self, token=None):
        self.name = token.text
        self.token = token

    def __str__(self):
        s = self.__repr__()
        s += "\n"
        s += self.context.error_info(self.token)
        return s


class IntParseError(BaseTypesError):
    def __repr__(self):
        return "Невозможно воспринять строку `{}`" \
               " как число".format(self.name)


class StrParseError(BaseTypesError):
    def __repr__(self):
        return "Строка должна быть обёрнута в кавычки"


class IdentifierNameError(BaseTypesError):
    def __repr__(self):
        return "Идентификатор должен состоять из букв, цифр и `_`. " \
               "Цифра не должна стоять на первом месте. Обнаружено: `{}`".format(self.name)


class AddressError(BaseTypesError):
    def __repr__(self):
        return "Адрес должен быть либо строкой вида `:32`, либо " \
               "идентификатором из текущего пространства имён." \
               " Обнаружено: `{}`".format(self.name)


class TypeNameError(BaseTypesError):
    def __repr__(self):
        return "Не могу найти тип `{}`".format(self.name)


class FunctionLifeTimeError(BaseTypesError):
    def __repr__(self):
        # TODO: Добавить возможные модификаторы
        return "Не могу найти модификатор времени жизни `{}`".format(
            self.name
        )
