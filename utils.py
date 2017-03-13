def clear_list(source: list):
    return [element for element in source if element]


def _get_quote(s: str):
    return s[s.find('"') + 1: s.rfind('"')]
