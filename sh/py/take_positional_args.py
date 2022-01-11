"""
Input: argv, `n *args`
Output: stdout, first `n` positional arguments in `args` that aren't preceded by ` -- `, one per line.
"""

import sys
import itertools

args = sys.argv[1:]

n = int(args.pop(0))

args = [
    arg
    for arg in itertools.takewhile(lambda arg: arg != '--', args)
    if not arg.startswith('--')
]
head = []
tail = []
stop = False
for arg in args:
    if len(head) < n and not arg.startswith('--') and not stop:
        head.append(arg)
    else:
        tail.append(arg)
        if arg == '--':
            stop = True

print(*args[:n], sep='\n')
