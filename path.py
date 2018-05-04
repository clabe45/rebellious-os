import re
# ERR, this uses circular referencing, but I don't know how to do it any different way; TODO: maybe use weakref

SEPARATOR = '/'
SPECIAL_CHARACTERS_ALLOWED = '_-.';
_SPECIAL_CHARACTERS_ALLOWED_REGEX = re.sub('-', '\\-', SPECIAL_CHARACTERS_ALLOWED)

class Path():
	def __init__(self, name, parent, validate_name=True):
		if validate_name: self.set_name(name)
		else: self.name = name
		self.parent = parent

	def set_name(self, new):
		if not re.match(r'^[a-zA-Z0-9 {}]+$'.format(_SPECIAL_CHARACTERS_ALLOWED_REGEX), new): 	# TODO: maybe extend in the future
			raise ValueError('Invalid name: ' + new + '!')
		if new.endswith('.'): raise ValueError("Name cannot end with '.'")
		self.name = new

	def move(self, path):
		self.parent.remove_child(self.name)
		path.put_child(self)

	def rename(self, new):
		# the following tests only apply to <em>re</em>naming a path, NOT initiating it with a name
		try:
			if self == root: return
		except NameError: pass	# root isn't defined yet
		if new == '': raise ValueError("Name cannot be empty!")

		self.parent.remove_child(self.name)
		self.set_name(new)
		self.parent.put_child(self)

	def _get(self, p):
		"""Gets the Path descendent with the specified relative path ``p``"""

		tokens = p.split(SEPARATOR)
		next_child = self.get_child(tokens[0])
		if len(tokens) > 1:
			if not type(next_child) is Directory:
				raise DirectoryException(str(self) + (SEPARATOR + next_child) if next_child else '')	# if File or None
			return next_child._get(SEPARATOR.join(tokens[1:]))
		return next_child

	def _put(self, p, contents):
		"""Puts the a new Path with contents to the specified relative path ``p``"""

		tokens = p.split(SEPARATOR)
		if len(tokens) > 1:
			next_child = self.get_child(tokens[0])
			if not type(next_child) is Directory:
				raise DirectoryException(str(self) + (SEPARATOR + next_child) if next_child else '')	# if File or None
			next_child._put(SEPARATOR.join(tokens[1:]), contents)
		else:
			path = None
			if type(contents) is str: path = File(tokens[0], self)
			elif type(contents) is dict: path = Directory(tokens[0], self)
			else: raise TypeError()	# TODO: include types in function definition ??
			self.put_child(path)

	def _remove(self, p):
		"""Removes the Path descendent with the specified relative path ``p``"""

		tokens = p.split(SEPARATOR)
		if len(tokens) > 1:
			next_child = self.get_child(tokens[0])
			if not type(next_child) is Directory:
				raise DirectoryException(str(self) + (SEPARATOR + next_child) if next_child else '')	# if File or None
			next_child._remove(SEPARATOR.join(tokens[1:]), contents)
		else: self.remove_child(p)

	def __tokens(self):
		"""Converts to a list of tokens in absolute path"""

		return (self.parent.__tokens() if self.parent else []) + [self.name]
	def __str__(self):
		"""Converts to an absolute path"""

		tokens = self.__tokens()
		return SEPARATOR if len(tokens) == 1 else SEPARATOR.join(tokens)

class File(Path):
	def __init__(self, name, parent, validate_name=True):
		super().__init__(name, parent, validate_name)
		self.data = ''

class Directory(Path):
	def __init__(self, name, parent, validate_name=True):
		super().__init__(name, parent, validate_name)
		self.children = {}
	def put_child(self, child): self.children[child.name] = child
	def get_child(self, name):
		if name == '.': return self
		if name == '..': return self.parent
		try: return self.children[name]
		except KeyError: raise NotFoundException((str(self) + SEPARATOR if self.name else '') + name)
	def has_child(self, name):
		if name == '.': return self
		if name == '..': return self.parent
		return name in self.children
	def remove_child(self, name):
		if name in ('.', '..'): raise ValueError('Cannot remove current working directory or its parent!')
		try: del self.children[name]
		except KeyError: raise NotFoundException((str(self) + SEPARATOR if self.name else '') + name)
	def __del__(self):
		for child in self.children: del child

def get(p, t=None):
	"""Get the Path instance with the specified path

	p -- (str) the relative or absolute path
	"""
	path = None
	if p.startswith(SEPARATOR):
		# absolute path
		path = root._get(p[1:])
	else:
		# relative path
		path = cwd._get(p)
	if t and type(path) != t: raise ValueError("'%s' is not a %s!" % (p, 'file' if t==File else 'directory'))
	return path

def create(p, contents):
	"""Create a Path instance with the ``contents`` and puts it in the path ``p``

	p -- (str) the relative or absolute path
	contents -- (str|dict) this determines whether it is a file or a directory;
		either the string contents of a file, or a dict of children for a directory
	"""

	tokens = p.split(SEPARATOR)
	location, name = tokens[:-1], tokens[-1]
	if has(p): raise DuplicateException(name)

	if p.startswith(SEPARATOR):
		# absolute path
		root._put(p[1:], contents)
	else:
		# relative path
		cwd._put(p, contents)

def remove(p):
	if p.startswith(SEPARATOR):
		# absolute path
		root._remove(p[1:])
	else:
		# relative path
		cwd._remove(p)

def has(p):
	"""Check whether a Path instance at path ``p`` exists

	p -- (str) the relative or absolute path
	"""

	if p.startswith(SEPARATOR):
		# absolute path
		try: root._get(p[1:])
		except (NotFoundException, DirectoryException): return False
		return True
	else:
		# relative path
		try: cwd._get(p)
		except (NotFoundException, DirectoryException): return False
		return True

def join(tokens):
	return SEPARATOR.join(tokens)
def split(p):
	return SEPARATOR.split(p)
def rstrip(p):
	return p.rstrip(SEPARATOR)

class IOException(Exception): pass	# note: different than IOError
class NotFoundException(IOException): pass
class DuplicateException(IOException): pass	# needed ?
class DirectoryException(IOException):
	"""When a nonexistent directory is used as a parent"""
	pass

root = Directory('', None, False)
cwd = root
