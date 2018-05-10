# tests if `bool1` and `bool2` are 'true'
# <bool1> <bool2>
#

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise ArgumentCountException()
result = True
for arg in argv:
    if arg not in ('true', 'false'): raise ArgumentException("'%s' is not a boolean value" % arg)
    b = arg == 'true'
    result = result and b
print(str(result).lower())
