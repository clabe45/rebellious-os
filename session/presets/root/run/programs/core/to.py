# changes the current working directory to `dir`
# <dir>
# _

if stdin and len(argv) == 0: argv.append(stdin)
if len(argv) != 1: raise ArgumentCountException()
p = argv[0]
silent = '_' in options
try:
    dir_ = path.get(p, path.Directory)
    path.cwd = dir_
except PathException as e:  # I could also list out (path.NotFoundException,path.DirectoryException) but it's less readable
    if not silent: raise e
