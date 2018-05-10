# negates `bool`
# <bool>
# 

if stdin and len(argv) == 0: argv.append(stdin)
if len(argv) != 1: raise ArgumentCountException()
if argv[0] not in ('true', 'false'): raise ArgumentException("'%s' is not a boolean value" % argv[0])
b = argv[0] == 'true'
print(str(not b).lower())
