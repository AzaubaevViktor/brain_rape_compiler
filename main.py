from br_compiler import BrCompiler
from executor import Interpreter

if __name__ == "__main__":
    compiler = BrCompiler('test_files/register/3.br')
    print("==== LINES: ====")
    for expr in compiler.lines:
        print(expr)

    print(compiler.block)

    print(
        "\n".join(
            compiler.block.debug_print()
        )
    )

    bytecode = compiler.compile()
    print()
    print("==== BYTECODE: ====")
    for code, func, expr in bytecode:
        for act in code:
            print(act, end=" ")
        print()
        print(func)
        print(expr)
        print("------")

    print()
    print("==== BRAINFUCK ====")
    for code, *_ in bytecode:
        for act in code:
            print(act.compile(), end="")
        print()
    print()

    print("==== EXECUTE ====")
    bytecode_clear = []
    for bytecode_line in bytecode:
        bytecode_clear += bytecode_line[0]
    interpreter = Interpreter(bytecode_clear)

    try:
        while True:
            interpreter.step()
    except EOFError:
        pass

    print(interpreter.memory)

