# nadove-git-config

This is where I keep the aliases for my `.gitconfig` file so I can synchronize 
them between computers. This is intended purely for personal use, so feel to 
copy my ideas but don't expect any sort of stability or backwards compatibility.

# Dependencies

Implemented in pure python 3 with no external libraries. Current revision was 
developed using 3.9.6.

# Installation/update

Simply clone the repository and run `make`. This overwrites the `[alias]` 
section of `~/.gitconfig`, creating it at the end of the file if necessary.
The contents of the old file are preserved in `~/.gitconfig.old`.

For (slightly) more flexible behavior, see `python3 update.py --help`.
