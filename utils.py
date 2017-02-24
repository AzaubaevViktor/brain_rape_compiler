import io


def clear_list(source: list):
    return [element for element in source if element]


def _get_quote(s: str):
    return s[s.find('"') + 1 : s.rfind('"')]


def get_tests(file_name):
    memory_tests = []
    memory_dict_test = {}
    inp = None
    out = None
    with open(file_name, 'rt') as f:
        lines = f.readlines()
        for line in lines:
            if "#!" != line[:2]:
                continue
            tokens = line.split(" ")[1:]
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
    return memory_tests, memory_dict_test, inp, out
