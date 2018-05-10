# prints the contents of `file`
# <file>`
#

if stdin and len(argv) == 0: argv.append(stdin)
if len(argv) != 1: raise ArgumentCountException()
p = argv[0]
file = path.get(p, path.File)
print(file.read())
