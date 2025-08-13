## Good first issues / status:

### Utils
`log.py`: small bug in `level` function. needs convenient way of effectively keeping track of file names for log messages from different/multiple files. also needs more typing support / warning ignores

### Builtins:

`ti_draw.py`: good enough, but not buggy enough like the real ti nspire version

`ti_system.py`: good enough, may need typing support

### Python-based virtual OS:

`filesys.py`: good enough

`fileio.py`: potential bug in `edit` and new line creation. spaghetti code needs fixing. current list <-> buffer manipulation is inefficient and may not work for large files.

`cli.py`: needs support for line wrapping for long lines.

`femto.py`: bug in `edit` and new line creation. can't save file to persistent memory

`main.py`: needs more integration with `fileio.py` for persistent folder/file storage