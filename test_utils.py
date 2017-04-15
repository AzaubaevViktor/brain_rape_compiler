import io

from utils import clear_list, _get_quote


class UnknownTest(Exception):
    def __init__(self, test_name: str):
        self.test_name = test_name

    def __str__(self):
        return "Неизвестный тип теста: {test_name}".format(
            test_name=self.test_name
        )


class BrTests:
    def __init__(self,
                 memory: list,
                 memory_dict: dict,
                 inp: io.StringIO,
                 out: io.StringIO,
                 exc_name: str
                 ):
        self.memory = memory
        self.memory_dict = memory_dict
        self.inp = inp
        self.out = out
        self.exc_name = exc_name


def get_tests(file_name) -> BrTests:
    """
    В файле можно указывать:
    
    #~test_MEMORYL 0 0 0 10 _ _ 5
    Числа проверяет, пропуски не проверяет
    
    #~test_MEMORYD memory_index memory_value
    Проверяет только одну пару
    
    #~test_INPUT "ololo"
    Данные, которые вводятся в программу
    
    #~test_OUTPUT "ololo"
    Данные, которые выводятся из программы
    
    #~test_EXCEPTION exception_class_name
    Проверяет, что выброшено исключение
    
    :param file_name: 
    :return: 
    """
    memory_tests = []
    memory_dict_test = {}
    exc_name = None
    inp = None
    out = None
    with open(file_name, 'rt') as f:
        lines = f.readlines()
        for line in lines:
            if "#~" != line[:2]:
                continue
            tokens = clear_list(line.split(" ")[1:])
            if "test_MEMORYL" == tokens[0]:
                memory_tests.append(
                    [int(x) if x != "_" else -1 for x in tokens[1:]]
                )
            elif "test_MEMORYD" == tokens[0]:
                memory_dict_test[int(tokens[1])] = int(tokens[2])
            elif "test_INPUT" == tokens[0]:
                inp = io.StringIO(_get_quote(line))
            elif "test_OUTPUT" == tokens[0]:
                out = io.StringIO(_get_quote(line))
            elif "test_EXCEPTION" == tokens[0]:
                exc_name = tokens[1]
            else:
                raise UnknownTest(tokens[0])
    return BrTests(memory_tests,
                   memory_dict_test,
                   inp,
                   out,
                   exc_name
                   )
