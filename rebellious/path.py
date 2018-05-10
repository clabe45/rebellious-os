import re
# ERR, this uses circular referencing, but I don't know how to do it any different way; TODO: maybe use weakref
# NOTE to self: beware of NotFoundException,DuplicateException,etc. because the str() representations *may be inaccurate*.
# For instance, if there's an empty string or something in processing, than it will still display the error as the full input
# TODO: maybe remove '/.'s and '/..'s from error messages when raising them in top-level functions (get, create, etc.)

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

		self.parent.remove_child(self.name)
		self.set_name(new)
		self.parent.put_child(self)

	# TODO: add has, probably
	def get(self, p, t=None):
		"""Get the Path descendent with the specified relative path ``p``"""

		if p.endswith(SEPARATOR): p = p[:-1]
		tokens = p.split(SEPARATOR)
		next_child = self.get_child(tokens[0])
		if len(tokens) > 1:
			if not type(next_child) is Directory:
				raise DirectoryException(str(self) + (SEPARATOR + next_child) if next_child else '')	# if File or None
			return next_child.get(SEPARATOR.join(tokens[1:]), t)
		if t and not type(next_child) is t: raise PathException("'%s' is not a %s!" % (p, 'file' if t==File else 'directory'))
		return next_child

	def has(self, p, t=None):
		try:
			self.get(p, t)
			return True
		except PathException:
			return False

	def create(self, p, t):
		"""Create a new Path of type ``t`` and put it to the specified relative path ``p``"""

		if p.endswith(SEPARATOR): p = p[:-1]
		tokens = p.split(SEPARATOR)
		if len(tokens) > 1:
			next_child = self.get_child(tokens[0])
			if not type(next_child) is Directory:
				raise DirectoryException(str(self) + (SEPARATOR + next_child) if next_child else '')	# if File or None
			return next_child.create(SEPARATOR.join(tokens[1:]), t)
		else:
			path = t(tokens[0], self)
			self.put_child(path)
			return path

	def remove(self, p):
		"""Remove the Path descendent with the specified relative path ``p``"""

		if p.endswith(SEPARATOR): p = p[:-1]
		tokens = p.split(SEPARATOR)
		if len(tokens) > 1:
			next_child = self.get_child(tokens[0])
			if not type(next_child) is Directory:
				raise DirectoryException(str(self) + (SEPARATOR + next_child) if next_child else '')	# if File or None
			next_child.remove(SEPARATOR.join(tokens[1:]))
		else: self.remove_child(p)

	def __get_tokens(self):
		"""Convert to a list of tokens in absolute path"""

		return (self.parent.__get_tokens() if self.parent else []) + [self.name]
	def __str__(self):
		"""Converts to an absolute path"""

		tokens = self.__get_tokens()
		return SEPARATOR if len(tokens) == 1 else SEPARATOR.join(tokens)

class File(Path):
	def __init__(self, name, parent, validate_name=True):
		super().__init__(name, parent, validate_name)
		self.data = ''
	def read(self):
		return self.data
	def write(self, data, append=False):
		if append: self.data += data
		else: self.data = data
	def flush(self): pass

class Directory(Path):
	def __init__(self, name, parent, validate_name=True):
		super().__init__(name, parent, validate_name)
		self.children = {}

	def put_child(self, child): self.children[child.name] = child

	def get_child(self, name):
		if name == '.': return self
		if name == '..': return self.parent if self.parent else self
		if name.endswith(SEPARATOR): name = name[:-1]
		try: return self.children[name]
		except KeyError: raise NotFoundException()			# str will be formed in the main functions (get, has, ...)

	def has_child(self, name):
		if name == '.': return True
		if name == '..': return True	# if self is root, than just take root
		if name.endswith(SEPARATOR): name = name[:-1]
		return name in self.children

	def remove_child(self, name):
		if name in ('.', '..'): raise ValueError('Cannot remove current working directory or its parent!')
		if name.endswith(SEPARATOR): name = name[:-1]
		try: del self.children[name]
		# this str will be cleaned up in the main functions
		except KeyError: raise NotFoundException()

	def __del__(self):
		try:
			for child in self.children: del child
		except AttributeError: pass 		# hasn't been fully initiated, so ignore this part

def get(p, t=None):
	"""Get the Path instance with the specified path

	p -- (str) the relative or absolute path
	"""
	if p == SEPARATOR and t != File: return root	# TODO: check if this belongs anywhere else too
	try:
		path = None
		if p.startswith(SEPARATOR):
			# absolute path
			return root.get(p[1:])
		else:
			# relative path
			return cwd.get(p)
	except PathException as e: raise type(e)(p)

def create(p, t):
	"""Create a Path instance of type ``t`` and put it in the path ``p``

	p -- (str) the relative or absolute path
	t -- (class) ``File`` or ``Directory``
	"""

	tokens = p.split(SEPARATOR)
	location, name = tokens[:-1], tokens[-1]
	if has(p): raise DuplicateException(name)

	try:
		if p.startswith(SEPARATOR):
			# absolute path
			return root.create(p[1:], t)
		else:
			# relative path
			return cwd.create(p, t)
	except DirectoryException as e: raise DirectoryException(p)	# use relative path

def remove(p):
	try:
		if p.startswith(SEPARATOR):
			# absolute path
			root.remove(p[1:])
		else:
			# relative path
			cwd.remove(p)
	except PathException as e: raise type(e)(p)

def has(p, t=None):
	"""Check whether a Path instance at path ``p`` exists

	p -- (str) the relative or absolute path
	"""

	try:
		if p.startswith(SEPARATOR):
			# absolute path
			return root.has(p[1:])
		else:
			# relative path
			return cwd.has(p)
	except DirectoryException: raise DirectoryException(p)

# TODO: figure out how to pass multiple args as on value in Python
def join(path, *paths):
	return SEPARATOR.join((path,) + paths)
def split(p):
	return SEPARATOR.split(p)
def rstrip(p):
	return p.rstrip(SEPARATOR)

class PathException(Exception): pass	# note: different than IOError
class NotFoundException(PathException): pass
class DuplicateException(PathException): pass	# needed ?
class DirectoryException(PathException):
	"""When a nonexistent directory is used as a parent"""

	pass


from os import listdir, mkdir
import os.path

def load(real_path, parent=None):
	"""Load an external path on the disk and convert it into a virtual path.

	real_path -- (str)
	parent -- (Directory)
	"""

	name = os.path.basename(real_path)
	if os.path.isdir(real_path):
		dir_ = Directory(name, parent)
		dir_.children = {child: load(os.path.join(real_path, child), dir_) for child in listdir(real_path)}
		return dir_
	real_file = open(real_path, 'r')
	file = File(name, parent)
	file.write(real_file.read())
	real_file.close()
	return file

def save(path, real_parent):
	"""Save a virtual path to the disk.

	path -- (Path)
	real_parent -- (str) directory
	"""

	full = os.path.join(real_parent, path.name)
	if type(path) is Directory:
		if not os.path.exists(full): mkdir(full)
		for child in path.children.values():
			save(child, full)
	else:
		real_file = open(full, 'w')
		real_file.write(path.read())
		real_file.close()

# TODO: maybe implicitely add child to parent when parent path is provided in constructor

def load_session(session):
	global root, cwd
	root = load(os.path.join('session', session, 'root'))
	root.name = ''	# don't use set_name, because it validates it, and don't use rename because of that and root has no parent

	cwd = root

def save_session():
	root.name = 'root'	# just for saving it
	dest = os.path.join('session', 'current')
	if not os.path.exists(dest): mkdir(dest)
	save(root, dest)

root = None
cwd = None

# load root (and cwd) in session.py
