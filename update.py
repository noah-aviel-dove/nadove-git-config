#!/usr/bin/python3

"""
Overwrites the [alias] section of a .gitconfig file,
optionally preserving the old version by appending a suffix to its file name.
"""

import argparse
import re
import shutil
import sys
import tempfile

import arg_types
from make_scripts import bash_script_prefix

alias_section_pattern = re.compile(r'^\[alias]')
other_section_pattern = re.compile(r'^\[\w+]')

indent = ' ' * 4

bash_hook = '#!bash'


def update_aliases(
    old_config_file,
    alias_file,
    new_config_file
) -> None:
    for config_line in old_config_file:
        new_config_file.write(config_line)
        if re.match(alias_section_pattern, config_line):
            break
    else:
        new_config_file.write('[alias]\n')

    for alias in alias_file:
        cmd, _, subst = alias.partition('=')
        subst = subst.strip()
        if subst == bash_hook:
            script = bash_script_prefix + cmd
            new_config_file.write(f'{indent}{cmd} = !{script}\n')
        else:
            new_config_file.write(indent + alias)

    for config_line in old_config_file:
        if re.match(other_section_pattern, config_line):
            new_config_file.write(config_line)
            break

    for config_line in old_config_file:
        new_config_file.write(config_line)

    new_config_file.flush()


def main(argv):
    parser = argparse.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument(
        'config_file_path',
        help='The existing configuration file to update',
        type=arg_types.file_path,
    )
    parser.add_argument(
        'alias_file_path',
        help='The file containing to new sh',
        type=arg_types.file_path,
    )
    parser.add_argument(
        '-B',
        '--backup-suffix',
        default='.old',
        help='The suffix to be appended to the backup of the old configuration file. '
             'Blank (-B \'\') means no backup.',
    )
    args = parser.parse_args(argv)

    old_config_path = args.config_file_path
    alias_path = args.alias_file_path
    backup_suffix = args.backup_suffix

    with tempfile.NamedTemporaryFile('w', delete=False) as new_config_file, \
        open(old_config_path, 'r') as old_config_file, \
        open(alias_path, 'r') as alias_file:
        update_aliases(
            old_config_file,
            alias_file,
            new_config_file
        )

        if backup_suffix:
            shutil.move(
                old_config_path,
                str(old_config_path) + backup_suffix,
            )

        shutil.move(
            new_config_file.name,
            old_config_path,
        )


if __name__ == '__main__':
    main(sys.argv[1:])
