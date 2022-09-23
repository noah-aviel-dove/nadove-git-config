"""
Input: argv, `n *args`
Output: stdout, first `n` positional arguments in `args` that aren't preceded by
` -- `, one per line, or an empty line if there are no such arguments.
Then all other args on one line.
"""

import sys

args = sys.argv[1:]

n = int(args.pop(0))

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

if not head:
    head.append('')

print(*head, ' '.join(tail), sep='\n')
