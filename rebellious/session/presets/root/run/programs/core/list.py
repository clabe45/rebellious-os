# lists the files in the current working directory, or `dir` if given
# [dir]
#

if stdin and len(argv) == 0: argv.append(stdin)
if len(argv) > 1: raise run.ArgumentCountException()
p = argv[0] if len(argv) == 1 else None
dir_ = path.get(p) if p else path.cwd
dirs = [name for name in dir_.children if type(dir_.children[name]) is path.Directory]
dirs.sort()
others = [name for name in dir_.children if not type(dir_.children[name]) is path.Directory]
others.sort()
print('\t'.join(dirs + others)) # TODO: maybe format better in the future
