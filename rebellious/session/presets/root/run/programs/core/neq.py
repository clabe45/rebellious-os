# 'tests if `val1` doesn\'t equal `val2`
# <val1> <val2>
#

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise run.ArgumentCountException()
try:
    print(str(num(argv[0]) != num(argv[1])).lower())
except ValueError as e:
    print(str(argv[0] != argv[1]).lower())
