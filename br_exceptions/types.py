from br_exceptions.base import BaseBrException


class BaseTypesException(BaseBrException):
    def __init__(self, token=None):
        self.name = token.text
        self.token = token


class IdentifierNameErrorException(BaseTypesException):
    def __str__(self):
        return "Идентификатор должен состоять из букв, цифр и `_`. " \
               "Цифра не должна стоять на первом месте. `{}`".format(self.name)


class AddressErrorException(BaseTypesException):
    def __str__(self):
        return "Адрес должен быть либо строкой вида `:32`, либо " \
               "идентификатором из текущего пространства имён." \
               " Обнаружено: `{}`".format(self.name)



class TypeNameErrorException(BaseTypesException):
    def __str__(self):
        return "Не могу найти тип `{}`".format(self.name)


class FunctionLifeTimeErrorException(BaseTypesException):
    def __str__(self):
        # TODO: Добавить возможные модификаторы
        return "Не могу найти модификатор времени жизни `{}`".format(
            self.name
        )
