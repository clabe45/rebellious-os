# prints `msg` or an empty iine to the screen
# [msg]
#

if stdin: print(stdin)
else:
    if len(argv) > 1: raise run.ArgumentCountException()
    print(argv[0] if len(argv) == 1 else '')
