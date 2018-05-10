# tests if `bool1` or `bool2`
# <bool1> <bool2>
#

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise ArgumentCountException()
result = False
for arg in argv:
    if arg not in ('true', 'false'): raise ArgumentException("'%s' is not a boolean value" % arg)
    b = arg == 'true'
    result = result or b
print(str(result).lower())
