# PyNspire

A collection of useless and fun Python programs in TI Nspire CX II calculators (version 6.0+ which is not compatible with Ndless)

Currently, a lot of the programs (and those I haven't uploaded) are buggy, and PRs (and issues) are extremely welcome. Status / good first issues can be found in STATUS.md

## Contribution / Development

If you have a product key for the calculator, you can simply paste the codes into a tns file's notes. Remember indentation on the calculator is actually 2 spaces.

If you do not, like me, have or want to buy one, you can test programs on your computer via the replicated and adapted builtins libraries. For actual production, you have to manually type / change code by hand, since no FOSS `.tns` file manipulator exists. Also, [Ndless](https://github.com/ndless-nspire/Ndless) dropped support for Version 6+.

## Documentation

### Builtins

`ti_draw.py`: drawing api for ti nspire. core part of projects

`ti_system.py`: ti nspire calculator and system api for system info / time, as well as storing and retrieving variables and lists to and from the ti nspire calculator page.

### Python-based virtual OS

`filesys.py`: stores the tree-node like structure for a file system. serves as 'backend' for the OS

`fileio.py`: handles persistent memory storage via ti_system apis.

`cli.py`: renders cli screen, object oriented -> can be passed around for different applications in the OS for control of screen rendering.

`femto.py`: stepwise command based text editor.

`main.py`: starts the program, parses commands

