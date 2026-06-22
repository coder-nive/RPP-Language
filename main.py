import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter, RPPError


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py program.rpp")
        sys.exit(1)
    path = sys.argv[1]
    try:
        tokens = Lexer(path).tokenize()
        ast = Parser(tokens).parse()
        interp = Interpreter()
        interp.run(ast)
        # if GUI windows were created, wait for them to close before exiting
        try:
            if hasattr(interp, 'windows'):
                interp.windows.wait_all()
        except Exception:
            pass
    except RPPError as e:
        print(f"R++ Error:\nLine {e.line if hasattr(e,'line') else '?'}\n{e}")
        sys.exit(2)
    except Exception as e:
        print("Unhandled error:", e)
        sys.exit(3)


if __name__ == '__main__':
    main()
