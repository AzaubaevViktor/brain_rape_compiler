def fill_str(s: str, fill_char: str, lenght: int):
    filled_len = (lenght - len(s) - 2) // 2
    added = (lenght - len(s) - 2) % 2

    return "{} {} {}".format(
        fill_char * (filled_len // len(fill_char)),
        s,
        fill_char * ((filled_len + added) // len(fill_char))
    )
