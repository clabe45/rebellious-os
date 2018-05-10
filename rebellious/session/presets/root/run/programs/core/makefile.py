# 'creates a file as `name`
# <name>
#

if stdin and len(argv) == 0: argv.append(stdin)
if len(argv) != 1: raise ArgumentCountException()
p = argv[0]
path.create(p, path.File)
