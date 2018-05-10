# changes the path of the item at `old` to `new`
# <old> <new>
# _

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise ArgumentCountException()
old, new = argv
silent = '_' in options
try:
    p = path.get(old)
    try:
        dest = path.get(new, path.Directory)
        if not (dest.has(p.name) and not silent and not confirm('Overwrite file or directory \'%s\'?' % path.join(dest, p.name))):
            p.move(dest)
    except (path.NotFoundException, ValueError):
        if old == new and not silent: raise ArgumentException('Source cannot equal destination!')
        if not (p.parent.has(new) and not silent and not confirm('Overwrite file or directory \'%s\'?' % path.join(p.parent, new))):
            p.rename(new)
except (path.NotFoundException, path.DirectoryException) as e:
    if not silent: raise e
