# nadove-git-config

This is where I organize and develop my git aliases. This is intended purely for
personal use, so feel to copy my ideas but don't expect any sort of stability or
backwards compatibility.

# Dependencies

Implemented in pure python 3 and bash with no external libraries. The current
revision was developed using python 3.10.4 and bash 5.1.16.

Many aliases reference other aliases and thus require git>=2.20.

Developed on and for Arch Linux, probably(?) works on other linuxes but no
promises

# Installation/update/removal

Clone the repository and run

    source environment
    make install

This will add a line to `~/.bashrc` to edit `PATH` and edit the global git
configuration.

To install updates, run

    source environment
    git pull
    make update

If you never use do anything more than that, then you can remove the aliases by
running

    source environment
    make uninstall

For info on more fine-grained behavior, run

    source environment
    make help


Some aliases rely on the concept of a default branch. In order for these
aliases to function, a value must be explicitly configured for
`init.defaultBranch`, e.g.

    git config init.defaultBranch develop

This configuration can be done on a per-project using `--local`, `--path`, etc.
Then run:

    source environment
    make update


# Disclaimer

Proceed at your own risk and please make sure you understand the source of the
more complicated commands before running them, as some of them do things like
force-pushing.
