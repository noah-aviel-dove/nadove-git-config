# nadove-git-config

This is where I keep the aliases for my `.gitconfig` file so I can synchronize 
them between computers. This is intended purely for personal use, so feel to 
copy my ideas but don't expect any sort of stability or backwards compatibility.

# Dependencies

Implemented in pure python 3 and bash with no external libraries. The current
revision was developed using python 3.9.6 and bash 5.1.8.

Many aliases reference other aliases and thus require git>=2.20.

# Installation/update

Clone the repository and run `make`. This overwrites the `[alias]`
section of `~/.gitconfig`, creating it at the end of the file if necessary.
The contents of the old file are preserved in `~/.gitconfig.old`.

Next, add the following to your `~/.bashrc`:

    export PATH=$PATH:<path_of_this_repo>/sh/cmds

And source `~/.bashrc`.

For (slightly) more flexible behavior, see `python3 update.py --help`.

# Disclaimer

Many of these commands make assumptions and take shortcuts that generally work
out for my own preferred workflows but are not generally applicable. The most
obvious example is the abundance of aliases that assume the existence of a
branch called `develop` which is an ancestor of the current branch. I am not
fixing this because I have no ambition of making these aliases suitable for
general use.

Proceed at your own risk and please make sure you understand the source of the
more complicated commands before running them, as some of them do things like
force-pushing.
