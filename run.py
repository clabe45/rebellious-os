import re
import math
import sys
import os

import cli
import path
import env
import internal
"""
TODO: change script and prog functions to store path (reference) instead of data (value), and remove update subcommand
and write files in a separate module (because this is getting huge!)
TODO: figure out whether to end every error with '!' or not (and which ones if not)
TODO: also figure out which commands should produce output and which ones shouldn't
TODO: sometime, make an update_aliases function when the alias list is modified, for caching the tokenized alias/syntax pairs
(for efficiency)
TODO: add <strike>copy</strike>, gt, lt, ge, lt commands
TODO: add documentation (descriptions) for the ^ option
TODO?: error wrong argument count, instead of no such command, with aliases with the wrong syntax (argument count)
"""

class Runnable():
	"""An object that can be run from the terminal"""

	def __init__(self, name, options, description, arg_usage):
		self.name = name
		# this way (using ``options`` as a separate value), there are no repeated substrings
		self.usage = '%s%s%s' % (name, (' (%s)'%options) if options else '', (' '+arg_usage) if arg_usage else '')
		self.description = description
		if path.SEPARATOR in options: raise ArgumentException("'%s' cannot be an option!" % path.SEPARATOR)
		self.options = options
	def execute(self, args, options, scope):
		for option in options:
			if option not in self.options: raise OptionException("Invalid option '%s'" % option)

class Program(Runnable):
	"""A native Runnable that uses Python code"""

	def __init__(self, name, options, arg_usage, description, fn):
		super().__init__(name, options, description, arg_usage)
		self.fn = fn
	def execute(self, args, options, scope):
		super().execute(args, options, scope)
		try:
			return self.fn(args, options, scope)
		except ArgumentCountException as e: raise ArgumentCountException(self.usage)
		except OptionException as e: raise OptionException('Invalid option \'%s\'; \'%s\'' % (str(e), self.usage))

class Script(Runnable):
	"""A primitive sequence of commands that can be run from the terminal, with a few special features"""

	def __init__(self, name, options, arg_usage, description, code):
		super().__init__(name, options, description, arg_usage)
		self.code = code
	def execute(self, args, options, scope):	# I think the ``scope`` arg is pretty much irrelevant
		super().execute(args, options, scope)
		statements = re.split(r'(?:\\\\)*(?!\\);', self.code)	# TODO: what if it's in a string??
		# TODO: change to 'argv' list when lists are supported
		local = {'arg%d'%i:arg for i,arg in enumerate(args)} # The local scope (varname=>str, value=>str)
		local['options'] = options
		for statement in statements:
			cli.process(statement, local)

def find_alias(tokens):
	"""return the syntax of the found alias or ``None``"""

	for syntax in aliases:
		s_statements = cli.tokenize(syntax)
		if len(s_statements) != 1: raise RuntimeError('Either zero or multiple statements in syntax: ' + syntax)
		s_tokens = s_statements[0]

		skip = False
		if len(tokens) != len(s_tokens): skip = True
		else:
			for x,_ in enumerate(s_tokens):
				if not s_tokens[x].isnumeric() and s_tokens[x] != tokens[x]:
					skip = True
					break
		if skip: continue

		return syntax
	return None

def fill_alias(syntax, tokens):
	"""replaces the argument symbols in ``syntax`` with the arguments in ``tokens``

	syntax -- **must be valid**
	tokens --
	return the final command to execute
	"""

	alias = aliases[syntax]
	args = {}	# map, so I can dynamically add items all over the place (the keys are the indexes)

	alias_statements = cli.tokenize(syntax)
	if len(alias_statements) != 1: raise RuntimeError('Either zero or multiple statements in alias: ' + alias)
	for x,token in enumerate(alias_statements[0]):
		if token.isnumeric():
			args[int(token)] = tokens[x]	# like args.put(x, tokens[0])

	result = alias	# result should look like alias, because alias is the end result
	for idx in args:
		result = re.sub(str(idx), args[idx], result)
	return result

"""
Builtin commands
"""
""" TODO: add '_' (silent) option to all commands that produce warning/information messages"""

# core system commands
def echo_function(args, options, scope):
	if len(args) != 1: raise ArgumentCountException()
	return args[0] if len(args) == 1 else ''
def shutdown_function(args, options, scope):
	if len(args) > 0: raise ArgumentCountException()
	print('*Shutting down...')
	internal.shutting_down = True
def list_function(args, options, scope):
	if len(args) > 1: raise ArgumentCountException()
	p = args[0] if len(args) == 1 else None
	dir = path.get(p) if p else path.cwd
	return '\t'.join([path for path in dir.children])
def to_function(args, options, scope):
	if len(args) != 1: raise ArgumentCountException()
	p = args[0]
	dir = path.get(p)
	if not type(dir) is path.Directory: raise ArgumentException("'%s' is not a directory!" % p)
	path.cwd = dir
def move_function(args, options, scope):	# TODO: *MOVE FILE*
	if len(args) != 2: raise ArgumentCountException()
	old, new = args
	silent = '_' in args
	try:
		p = path.get(old)
		try: p.move(path.get(new, path.Directory))
		except (path.NotFoundException, ValueError):
			if old == new and not silent: raise ArgumentException('Source cannot equal destination!')
			p.rename(new)
	except (path.NotFoundException, path.DirectoryException) as e:
		if not silent: raise e
def make_directory_function(args, options, scope):
	if len(args) != 1: raise ArgumentCountException()
	p = args[0]

	silent = '_' in options
	try: path.create(p, {})
	except (path.DuplicateException,path.DirectoryException) as e:
		if not silent: raise e
def make_file_function(args, options, scope):
	if len(args) != 1: raise ArgumentCountException()
	p = args[0]
	silent = '_' in options

	try: path.create(p, '')
	except (path.DuplicateException,path.DirectoryException) as e:
		if not silent: raise e
def delete_function(args, options, scope):
	if len(args) != 1: raise ArgumentCountException()
	for option in options:
		if option not in '_': raise OptionException(option)

	p = args[0]
	silent, recursive = '_' in options, '^' in options

	if not silent:
		if not confirm('*Delete file \'%s\'? ' % p): return
	try:
		if recursive: path.get(p, path.Directory)
		path.remove(p)	# the `recursive` options is for user clarity only
	except (path.NotFoundException,path.DirectoryException) as e:
		if not silent: raise e
def copy_function(args, options, scope):
	if len(args) != 2: raise ArgumentCountException()
	sourcep, destp = args
	source = path.get(sourcep)
	recursive = '^' in options		# just for user clarity
	if not recursive:
		copy_file(sourcep, destp)
	else:
		dest = path.create(destp, {}) if not path.has(destp) else path.get(destp)
		copy_dir_recursive(source, dest, '.')
def copy_dir_recursive(source, dest, rel_path):
	if rel_path != '.':
		# because root dest dir is created in copy_function
		dest.create(rel_path, {}) if not path.has(rel_path) else path.get(rel_path)
	source_child = source.get(rel_path)
	for name in source_child.children:
		if type(source_child.children[name]) is path.Directory:
			copy_dir_recursive(source, dest, rel_path + path.SEPARATOR + name)
		else:
			copy_file(
				path.join([source.name, rel_path + path.SEPARATOR + name]),
				path.join([dest.name, rel_path + path.SEPARATOR + name])
			)
def copy_file(sourcep, destp):	# let's just assume the args are valid
	source = path.get(sourcep, path.File)
	if not path.has(destp, path.File): path.create(destp, source.data)
	else: path.get(destp).data = source.data

def read_function(args, options, scope):
	if len(args) != 1: raise ArgumentCountException()
	p = args[0]
	file = path.get(p)
	if not type(file) is path.File: raise ArgumentException("'%s' is not a file!" % p)
	return file.data
def write_function(args, options, scope):
	if len(args) != 2: raise ArgumentCountException()

	p = args[0]
	file = path.get(p)
	if not type(file) is path.File: raise ArgumentException("'%s' is not a file!" % p)
	data = args[1]
	append = '+' in options

	if append:
		file.data += data
	else:
		file.data = data
def set_function(args, options, scope):
	if len(args) < 1: raise ArgumentCountException()
	global_ = '$' in options
	name = args[0]
	sc = env.variables if global_ else scope
	if len(args) == 2:
		value = args[1]
		sc[name] = value
	elif name in sc: del sc[name]
def get_function(args, options, scope):
	if len(args) != 1: raise ArgumentCountException()
	global_ = '$' in options
	name = args[0]
	try:
		sc = env.variables if global_ else scope
		return sc[name]
	except KeyError:
		return env.UNDEFINED_STRING
def clear_function(args, options, scope):
	os.system('cls' if os.name == 'nt' else 'clear')	# taken from https://stackoverflow.com/a/2084628/3783155
	print()	# empty line

# operators
# logical
def equal_function(args, options, scope):
	if len(args) != 2: raise ArgumentCountException()
	return str(args[0] == args[1]).lower()
def not_equal_function(args, options, scope):
	if len(args) != 2: raise ArgumentCountException()
	return str(args[0] != args[1]).lower()
def less_than_function(args, options, scope):
	if len(args) != 2: raise ArgumentException()
	silent = '_' in args
	try:
		return str(num(args[0]) < num(args[1])).lower()
	except ValueError as e:
		if not silent: raise e
def greater_than_function(args, options, scope):
	if len(args) != 2: raise ArgumentException()
	silent = '_' in args
	try:
		return str(num(args[0]) > num(args[1])).lower()
	except ValueError as e:
		if not silent: raise e
def less_than_equal_function(args, options, scope):
	if len(args) != 2: raise ArgumentException()
	silent = '_' in args
	try:
		return str(num(args[0]) <= num(args[1])).lower()
	except ValueError as e:
		if not silent: raise e
def greater_than_equal_function(args, options, scope):
	if len(args) != 2: raise ArgumentException()
	silent = '_' in args
	try:
		return str(num(args[0]) >= num(args[1])).lower()
	except ValueError as e:
		if not silnet: raise e
def not_function(args, options, scope):
	if len(args) != 1: raise ArgumentCountException()
	if args[0] not in ('true', 'false'): raise ArgumentException("'%s' is not a boolean value" % args[0])
	b = args[0] == 'true'
	return str(not b).lower()
def or_function(args, options, scope):
	if len(args) != 2: raise ArgumentCountException()
	result = False
	for arg in args:
		if arg not in ('true', 'false'): raise ArgumentException("'%s' is not a boolean value" % arg)
		b = arg == 'true'
		result = result or b
	return str(result).lower()
def and_function(args, options, scope):
	if len(args) != 2: raise ArgumentCountException()
	result = True
	for arg in args:
		if arg not in ('true', 'false'): raise ArgumentException("'%s' is not a boolean value" % arg)
		b = arg == 'true'
		result = result and b
	return str(result).lower()

# strings
def concat_function(args, options, scope):
	if len(args) < 2: raise ArgumentCountException()
	return ''.join(args)

# numbers
def add_function(args, options, scope):
	if len(args) < 2: raise ArgumentCountException()
	sum = 0
	for arg in args:
		try:
			sum += float(arg) if '.' in arg else int(arg)
		except ValueError: raise ArgumentException("'%s' is not a number!" % arg)
	return str(sum)
def subtract_function(args, options, scope):
	if len(args) != 2: raise ArgumentCountException()
	difference = 0
	for x,arg in enumerate(args):
		try:
			n = float(arg) if '.' in arg else int(arg)
			difference += n if x == 0 else -n
		except ValueError: raise ArgumentException("'%s' is not a number!" % arg)
	return str(difference)
def multiply_function(args, options, scope):
	if len(args) < 2: raise ArgumentCountException()
	product = 1
	for arg in args:
		try:
			product *= float(arg) if '.' in arg else int(arg)
		except ValueError: raise ArgumentException("'%s' is not a number!" % arg)
	return str(product)
def divide_function(args, options, scope):
	if len(args) != 2: raise ArgumentCountException()
	quotient = 1
	for x,arg in enumerate(args):
		try:
			n = float(arg)		# always returns float
			quotient *= n if x==0 else 1/n
		except ValueError: raise ArgumentException("'%s' is not a number!" % arg)
	return str(quotient)
def power_function(args, options, scope):
	if len(args) != 2: raise ArgumentCountException()
	try:
		base = float(args[0]) if '.' in args[0] else int(args[0])		# always returns float
		power = float(args[1]) if '.' in args[1] else int(args[1])		# always returns float
		result = base**power
		return str(int(result) if result % 1 == 0 else result)
	except ValueError: raise ArgumentException("'%s' is not a number!" % arg)
def root_function(args, options, scope):
	if len(args) != 2: raise ArgumentCountException()
	try:
		base = float(args[0]) if '.' in args[0] else int(args[0])		# always returns float
		root = float(args[1]) if '.' in args[1] else int(args[1])		# always returns float
		result = base**(1.0/root)
		return str(int(result) if result % 1 == 0 else result)
	except ValueError: raise ArgumentException("'%s' is not a number!" % arg)
def square_root_function(args, options, scope):
	if len(args) != 1: raise ArgumentCountException()
	try:
		x = float(args[1]) if '.' in args[0] else int(args[0])		# always returns float
		result = math.sqrt(x)
		return str(int(result) if result % 1 == 0 else result)
	except ValueError: raise ArgumentException("'%s' is not a number!" % arg)
def modulo_function(args, options, scope):
	if len(args) != 2: raise ArgumentException()
	try:
		dividend, divisor = float(args[0]), float(args[1])
		return dividend % divisor
	except ValueError: raise ArgumentException("'%s' is not a number!" % arg)

# commands for commands
def script_function(args, options, scope):
	if len(args) < 1: raise ArgumentCountException()
	subcommand = args[0]
	if subcommand == 'add':
		if len(args) != 5: raise ArgumentCountException()
		name, options, arg_usage, description = args[1:]
		file = path.get(name + '.' + SCRIPT_EXTENSION, path.File)
		scripts.add(Script(name, options, arg_usage, description, file.data))
		return '*Created script \'%s\'!' % name
	elif subcommand == 'update':
		if len(args) != 2: raise ArgumentCountException()
		name = args[1]
		file = path.get(name + '.' + SCRIPT_EXTENSION, path.File)
		script = get_script(name)
		script.code = file.data
		return '*Script \'%s\' updated sucessfully!' % name
	elif subcommand == 'remove':
		if len(args) < 2: raise ArgumentCountException()
		name = args[1]
		for script in scripts:
			if script.name == name:
				scripts.remove(script)
				return '*Script \'%s\' removed!' % name
		raise ArgumentException('No such script \'%s\'' % name)
	elif subcommand == 'list':
		return '\n'.join(["'%s': '%s', '%s'" % (s.name, s.options, s.usage) for s in scripts])
	else: raise ArgumentException('No such subcommand \'%s\'!' % subcommand)
def program_function(args, options, scope):
	if len(args) < 1: raise ArgumentCountException()
	subcommand = args[0]
	if subcommand == 'add':
		if len(args) != 5: raise ArgumentCountException()
		name, options, arg_usage, description = args[1:]
		file = path.get(name + '.' + PROGRAM_EXTENSION, path.File)
		programs.add(Program(name, options, arg_usage, description, _compile_program_fn(file.data)))
		return '*Created program \'%s\'!' % name
	elif subcommand == 'update':
		if len(args) != 2: raise ArgumentCountException()
		name = args[1]
		file = path.get(name + '.' + PROGRAM_EXTENSION, path.File)
		program = get_program(name)
		program.fn = _compile_program_fn(file.data)
		return '*Program \'%s\' updated sucessfully!' % name
	elif subcommand == 'remove':
		if len(args) < 2: raise ArgumentCountException()
		name = args[1]
		for program in programs:
			if program.name == name:
				programs.remove(program)
				return '*Program \'%s\' removed!' % name
		raise ArgumentException('No such program \'%s\'' % name)
	elif subcommand == 'list':
		return '\n'.join(["'%s': '%s', '%s'" % (p.name, p.options, p.usage) for p in programs])
	raise ArgumentException('No such subcommand \'%s\'' % subcommand)
def _compile_program_fn(code):
	def fn(args, options, scope):
		output = _Logger()
		cache, sys.stdout = sys.stdout, output
		try: exec(code, {}, {'args': args, 'options': options})
		except Exception as e: print('An error occured in script execution: %s' % str(e))
		sys.stdout = cache
		return str(output).rstrip('\n')
	return fn
class _Logger():
	def __init__(self):
		self.text = ''
	def write(self, s):
		self.text += s
	def flush(self): pass
	def __str__(self): return self.text
def alias_function(args, options, scope):
	if len(args) < 1: raise ArgumentCountException()
	subcommand = args[0]
	syntax = args[1] if len(args) > 1 else None
	if len(cli.tokenize(syntax) != 1): raise ArgumentException('Either zero or multiple statements in syntax: ' + syntax)
	if subcommand == 'set':
		if len(args) != 3: raise ArgumentCountException()
		alias = args[2]
		if len(cli.tokenize(alias) != 1): raise ArgumentException('Either zero or multiple statements in alias: ' + syntax)
		aliases[syntax] = alias
		return "Syntax '" + syntax + "' bound to '" + alias + "'"
	elif subcommand == 'get':
		if len(args) != 2: raise ArgumentCountException()
	elif subcommand == 'clear':
		if len(args) != 2: raise ArgumentCountException()
		del aliases[syntax]
		if confirm('Remove alias \'%s\'?' % syntax): return "Syntax '" + syntax + "' removed"
	elif subcommand == 'list':
		if len(args) != 1: raise ArgumentCountException()
		return '\n'.join(["'%s': '%s'" % (syntax, aliases[syntax]) for syntax in aliases])
	else: raise ArgumentException("No such alias function '%s'" % subcommand)
def help_function(args, options, scope):
	if len(args) > 1: raise ArgumentCountException()
	if len(args) == 0: return '\n'.join([program.name for program in programs])
	else:
		name = args[0]
		for program in programs:
			if program.name == name:
				return '%s - %s' % (program.usage, program.description)
		return 'No such program \'%s\'' % name

def confirm(prompt):
	p = ''
	while not p.lower() in ('y', 'n'):
		p = input('%s [Y/N] ' % prompt)
	return p.lower() == 'y'
def num(s):
	# credits -> https://stackoverflow.com/a/379966/3783155
	try:
		return int(s)
	except ValueError:
		return float(s)
	raise ValueError("'%s' is not a number!" % s)

SCRIPT_EXTENSION = 's'
PROGRAM_EXTENSION = 'p'
# TODO: add move command
programs = set([
	Program('echo', '', '<msg>', 'prints `msg` to the screen', echo_function),
	Program('shutdown', '', '', 'exits the current session', shutdown_function),
	Program('list', '', '[dir]', 'lists the files in the current working directory, or `dir` if given', list_function),
	Program('to', '', '<dir>', 'changes the current working directory to `dir`', to_function),
	Program('makedir', '_', '<name>', 'creates a directory as `name`', make_directory_function),
	Program('makefile', '_', '<name>', 'creates a file as `name`', make_file_function),
	Program('delete', '_^', '<path>', 'deletes the item at `path`, recursively if the `^` option is set', delete_function),
	Program(
		'copy', '_^', '<source> <dest>', 'copies the path at source to dest, recursively if the `^` option is set',
		copy_function
	),
	Program('move', '_', '<old> <new>', 'changes the path of the item at `old` to `new`', move_function),
	Program('read', '', '<file>', 'prints the contents of `file`', read_function),
	Program(
		'write', '+', '<path> <text>', 'writes the contents of the file at `path`, appending if `+` switch is set',
		write_function
	),
	Program(
		'set', '$', '<var> [value]', 'sets the environment variable `var` to `value`, or deletes if `value` is not provided',
		set_function
	),
	Program('clear', '', '', 'clears the screen', clear_function),
	Program('get', '$', '<var>', 'prints the environment variable `var`, exactly like \'echo <`var`>\'', get_function),
	Program('eq', '', '<val1> <val2>', 'tests if `val1` equals `val2`', equal_function),
	Program('neq', '', '<val1> <val2>', 'tests if `val1` doesn\'t equal `val2`', not_equal_function),
	Program('lt', '_', '<num1> <num2>', 'tests if `num1` is less than `num2`', less_than_function),
	Program('gt', '_', '<num1> <num2>', 'tests if `num1` is greater than `num2`', greater_than_function),
	Program('ge', '_', '<num1> <num2>', 'tests if `num1` is greater than or equal to `num2`', greater_than_equal_function),
	Program('le', '_', '<num1> <num2>', 'tests if `num1` is less than or equal to `num2`', less_than_equal_function),
	Program('not', '', '<bool>', 'negates `bool`', not_function),
	Program('or', '', '<bool1> <bool2>', 'checks if either `bool1` or `bool2` are \'true\' inclusively', or_function),
	Program('and', '', '<bool1> <bool2>', 'checks if both `bool1` and `bool2` are \'true\'', and_function),
	Program('concat', '', '<str1> <str2> [str3] ...', 'concatenates the strings in `str`', concat_function),
	Program('add', '', '<num1> <num2> [num3] ...', 'adds the numbers in `num`', add_function),
	Program('sub', '', '<num1> <num2>', 'prints `num1` - `num2`', subtract_function),
	Program('mul', '', '<num1> <num2> [num3] ...', 'multiplies the numbers in `num`', multiply_function),
	Program('div', '', '<num1> <num2>', 'prints `num1` / `num2`', divide_function),
	Program('pow', '', '<num1> <num2>', 'prints `num1` ^ `num2`', power_function),
	Program('root', '', '<num1> <num2>', 'prints the `num2` root of `num1`', root_function),
	Program('sqrt', '', '<num>', 'prints the square root of `num`', square_root_function),

	Program(
		'script', '', '<add|update|remove|list> [name] [options] [argument-usage] [description]',
		'modifies the list of system scripts', script_function
	),
	Program(
		'prog', '', '<add|update|remove|list> [name] [options] [argument-usage] [description]',
		'modifies the list of system programs', program_function
	),
	Program('alias', '', '<get|set|clear|list> [syntax] [alias]', 'modifiers the list of system aliases', alias_function),
	Program('help', '', '[runnable]', 'lists all commands, or displays information about `runnable`', help_function)
])

def get_program(name):
	for program in programs:
		if program.name == name: return program
	return None

scripts = set()

def get_script(name):
	for script in scripts:
		if script.name == name: return script
	return None

aliases = {
	'!!!': 'shutdown',
	'?': 'help',
	'0 -> 1': 'alias 0 1',
	'* 0': 'makefile 0',
	'^ 0': 'makedir 0',
	'+ 0 1': 'copy 0 1',
	'~ 0 1': 'move 0 1',
	'! 0': 'delete 0',
	'- 0': 'to 0',
	'/': 'list',	# TODO: make it smart so the user doesn't have to type in every possibility for syntax with aliases
	'/ 0': 'list 0',
	'0 = 1': 'set 0 1'
}

class RunException(Exception): pass
# I wish I could have this subclass ValueError, too, because it's a special version of a ValueError
class ArgumentException(RunException): pass
class ArgumentCountException(RunException): pass
class OptionException(RunException): pass
class NoSuchCommandException(RunException): pass
