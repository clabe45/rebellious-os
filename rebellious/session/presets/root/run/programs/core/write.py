# writes the contents of `file``, appending if `+` switch is set
# <file> <text>
# +


if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise run.ArgumentCountException()

p = argv[0]
file = path.get(p, path.File)
data = argv[1]
append = '+' in options

file.write(data, append)
