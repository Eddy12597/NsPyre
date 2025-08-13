## Good first issues / status

Here the issues and todos are listed with each file. (#) indicates expected difficulty

### Utils
`log.py`:

(1): small bug in `level` function 
(1): add typing support / warning ignores if working on ide / pylance
(1): needs convenient way of effectively keeping track of file names for log messages from different/multiple files.

`format.py`:

~~(1): provide implementation for printf~~

### Builtins:

`ti_draw.py`: 

(0): needs more thorough testing

`ti_system.py`:

(0): needs testing
(0): needs typing support

### Python-based virtual OS:

`filesys.py`:

(1): dir function is recursive by default when called from main

`fileio.py`: 

(1): potential bug in `edit` and new line creation. 
(2): spaghetti code needs fixing.
(3): current list <-> buffer manipulation is inefficient and may not work for large files.

`cli.py`:

(2): needs support for line wrapping for long lines.

`femto.py`: 

(2): bug in `edit` and new line creation.
(2): can't save file to persistent memory

`terminal.py`: 

(2): needs more integration with `fileio.py` for persistent folder/file storage
