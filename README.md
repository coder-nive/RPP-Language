# R++ (RPP) — A tiny interpreted language

This repository contains a small interpreter for the R++ language implemented in Python.
It is a language specificly made for GUIs!
R++ might have some bugs but we are still working on it!
License: R++ License
See the LICENSE file for details.

## Download

[Download ZIP File](https://www.golden-games.info/downloadR.html)

Download the latest release of R++ as a ZIP archive containing the complete Python source code, examples, and documentation.

Run a program with:

```bash
python main.py examples/example.rpp
```

Project layout:

- `main.py` — entrypoint
- `lexer.py` — tokenizes .rpp files line-by-line
- `parser.py` — converts lines into instruction nodes
- `interpreter.py` — executes nodes and maintains environment
- `stdlib/` — helper modules (gui, files, utils, variables)
- `examples/` — example programs

Features implemented:
- say, variables, set, varnew
- loops, if/else
- functions (definition + call)
- basic file operations (write/read/delete)
- random number generation
- wait
- simple GUI support using `tkinter` (windows, text, input, buttons, labels, notifications)
- imports (import another .rpp file)

Notes:
- This is a minimal, instructive implementation. It focuses on clarity and extendability rather than performance.
- Error messages include line numbers for easier debugging.
