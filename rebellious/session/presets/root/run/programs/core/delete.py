# deletes the item at `path
# <path>
# ^_

if stdin and len(argv) == 0: argv.append(stdin)
if len(argv) != 1: raise ArgumentCountException()

p = argv[0]
silent, recursive = '_' in options, '^' in options

try:
    file = path.get(p)
    if recursive: path.get(p, path.Directory)
    elif type(file) is path.Directory: raise ArgumentException('Please use the recursive flag `^` for directories.')
    cancel = not silent and not confirm('*Delete %s \'%s\'?' % ('file' if type(file) is path.File else 'directory', p))
    if not cancel: path.remove(p)	# the `recursive` options is for user clarity only
except (path.NotFoundException,path.DirectoryException) as e:
    if not silent: raise e
