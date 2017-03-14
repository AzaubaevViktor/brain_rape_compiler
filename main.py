from br_compiler import FileCompiler, Lexer
from executor import Interpreter

if __name__ == "__main__":
    file_name = 'test_files/exc/p_arg_len2.br'
    block = None
    with open(file_name, 'rt') as f:
        l = Lexer(f.readlines())

        print("==== LINES: ====")
        for expr in l.lines:
            print(expr)

        block = l.block

    print("=== BLOCK ====")
    print(block)

    print(
        "\n".join(
            block.debug_print()
        )
    )

    compiler = FileCompiler(file_name, block)

    compiler.compile()

    print("==== BYTECODE: ====")

    print(
        "\n".join(
            compiler.context.debug_print()
        )
    )

    print("==== BRAINFUCK ====")
    bytecode = compiler.context.full_bytecode()
    for code in bytecode:
        print(code.compile(), end="")
    print()

    print("==== EXECUTE ====")
    interpreter = Interpreter(bytecode)

    try:
        while True:
            interpreter.step()
    except EOFError:
        pass

    print()
    print("==== MEMORY ====")
    print(interpreter.memory)

