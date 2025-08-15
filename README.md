# PyNspire

A collection of useless and fun Python programs in TI Nspire CX II calculators (version 6.0+ which is not compatible with Ndless)

Currently, a lot of the programs (and those I haven't uploaded) are buggy, and PRs (and issues) are extremely welcome. Status / good first issues can be found in STATUS.md

## Contribution / Development

If you have a product key for the calculator, you can simply paste the codes into a tns file's notes. Remember indentation on the calculator is actually 2 spaces.

If you do not, like me, have or want to buy one, you can test programs on your computer via the replicated and adapted builtins libraries. For actual production, you have to manually type / change code by hand, since no FOSS `.tns` file manipulator exists. Also, [Ndless](https://github.com/ndless-nspire/Ndless) dropped support for Version 6+.

Type hints are, like in python, not checked in TI Nspire. The `|` syntax for a union of types is not supported and results in syntax error. However, you can emulate unions of types by `/` (TI Nspire python does not check for type validity, and for custom object types, you don't have to include quotes. In fact, that results in a syntax error). Type hints are not available for direct variable assignment (e.g. `a: dict[str,str] = {}`); you have to write comments for them.

Some useful keyboard shortcuts. You can type underscores (`_`) on the calculator very quickly by Ctrl + space, and you can type colons (`:`) quickly by Ctrl + symbols (the key that has a blue `:=` on top). Ctrl + del deletes the entire line, no matter where the cursor is. Ctrl + H is find and replace. Move between pages by ctrl + arrow. Always remember to save your entire `.tns` file by `doc + 1 + 4`, not just saving the python file (`menu + 2 + 2`).

For detailed listing of good first issues/PRs, see the Status section.

## Documentation

### Builtins

`ti_draw.py`: drawing api for ti nspire. core part of projects

`ti_system.py`: ti nspire calculator and system api for system info / time, as well as storing and retrieving variables and lists to and from the ti nspire calculator page.

### Python-based virtual OS

`filesys.py`: stores the tree-node like structure for a file system. serves as 'backend' for the OS

`fileio.py`: handles persistent memory storage via ti_system apis.

`cli.py`: renders cli screen, object oriented -> can be passed around for different applications in the OS for control of screen rendering.

`femto.py`: stepwise command based text editor.

`terminal.py`: starts the program, parses commands

---

## Status / Good first issues

Here the issues and todos are listed with each file. (#) indicates expected difficulty

### Utils
`log.py`:

(1): small bug in `level` function 

(1): add typing support / warning ignores if working on ide / pylance

(1): needs convenient way of effectively keeping track of file names for log messages from different/multiple files.

`format.py`:

~~(1): provide implementation for printf~~ (by [Eddy12597](https://github.com/Eddy12597))

### Builtins:

`ti_draw.py`: 

(3): figure out a calculator-compatible way for a blocking input function (try running `_test_cli.py` and you'll see)

`ti_system.py`:

(0): needs testing

(0): needs typing support

### Python-based virtual OS:

`filesys.py`:

~~(1): dir function is recursive by default when called from main~~ (by [Eddy12597](https://github.com/Eddy12597))

`fileio.py`: 

(1): potential bug in `edit` and new line creation. 

(2): spaghetti code needs fixing.

(3): current list <-> buffer manipulation is inefficient and may not work for large files.

`cli.py`:

(1): needs testing for support for line wrapping for long lines.

`femto.py`: 

(1): bug in `edit` function

(2): can't save file to persistent memory

`terminal.py`: 

(2): needs more integration with `fileio.py` for persistent folder/file storage
