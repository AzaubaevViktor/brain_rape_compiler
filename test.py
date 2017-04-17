import pytest

from br_lexer import FileStream, Lexer
from br_test import get_all_files, FileTest
from utils import fill_str


def test_file():
    file_test = None  # type: FileTest

    folder = "test"
    for filename in get_all_files(folder):
        global file_test
        print("\n")
        print(fill_str(
            "{}".format(filename.split("/")[-1]),
            fill_char="=",
            lenght=60
        ))
        print("Test file `{}`".format(filename))

        with open(filename, "rt") as f:
            file_test = FileTest(f.readlines())

        try:
            print("Description:\n {}".format(file_test.desc))

            stream = FileStream(filename)
            block, lines = Lexer.get_block(stream)

        except Exception as e:
            assert file_test.exception is not None, \
                "Выброшено исключение `{}`, его быть не должно".format(
                    e.__class__.__name__
                )

            assert e.__class__.__name__ == file_test.exception, \
                "Выброшено неверное исключение. " \
                "Ожидается `{}`, по факту `{}`".format(
                    file_test.exception,
                    e.__class__.__name__
                )
            print("Exception `{}` catched!".format(file_test.exception))
        else:
            assert file_test.exception is None, \
                "Пейн, я исключения не чувствую! `{}`".format(
                    file_test.exception
                )

if __name__ == "__main__":
    test_file()