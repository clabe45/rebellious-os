# copies the path at `source` to `dest`
# <source> <dest>
# ^

def copy_dir_recursive(source, dest, rel_path):
	if rel_path != '.':
		# because root dest dir is created in copy_function
		dest.create(rel_path, path.Directory) if not path.has(rel_path) else path.get(rel_path)
	source_child = source.get(rel_path)
	for name in source_child.children:
		if type(source_child.children[name]) is path.Directory:
			copy_dir_recursive(source, dest, rel_path + path.SEPARATOR + name)
		else:
			copy_file(
				path.join(source.name, rel_path + path.SEPARATOR + name),
				path.join(dest.name, rel_path + path.SEPARATOR + name)
			)

def copy_file(sourcep, destp):	# let's just assume the args are valid
	source = path.get(sourcep, path.File)
	dest = path.create(destp, path.File) \
		if not path.has(destp, path.File) \
		else path.get(destp)
	dest.write(source.read())


if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise ArgumentCountException()
sourcep, destp = argv
recursive = '^' in options		# just for user clarity
source = path.get(sourcep, path.Directory if recursive else None)
if not recursive:
	if type(source) is path.Directory:
		raise ArgumentException('Please use the recursive flag `^` for directories.')

	copy_file(sourcep, destp)
else:
	dest = path.create(destp, path.Directory) if not path.has(destp) else path.get(destp)
	copy_dir_recursive(source, dest, '.')
