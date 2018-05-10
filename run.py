import re
import math
import sys
import os
import os.path
import traceback
import json

# make sure to import all project modules (except main, and idk what to do about 'run.*' notation), for ease of use with `exec`ing
import cli
import env
import internal
import path
import session
"""
TODO: figure out whether to end every error with '!' or not (and which ones if not)
TODO: also figure out which commands should produce output and which ones shouldn't
TODO: sometime, make an update_aliases function when the alias list is modified, for caching the tokenized alias/syntax pairs
(for efficiency)
TODO-MORE?: add documentation (descriptions) for the ^ option
TODO?: error wrong argument count, instead of no such command, with aliases with the wrong syntax (argument count);
Maybe that's impossible because of the flexibility of aliases.
TODO: prevent built in programs from being deleted with PERMISSIONS
TODO?: figure out how to use ``run.ArgumentException`` instead of ``ArgumentException`` in programs
TODO: only use <varname> syntax in ``echo``?
"""

SCRIPT_EXTENSION = 's'
PROGRAM_EXTENSION = 'py'

class Runnable():
	"""An object that can be run from the terminal"""

	def __init__(self, file):
		self.name = file.name[:-len('.'+PROGRAM_EXTENSION)]
		self.path = str(file)	 # be careful not to set `path` because of the module
		docs = file.read().split('\n')[:3]
		for line in docs:
			if not line.startswith('#'): raise ValueError('Invalid documentation for program \'%s\'' % self.name)
		self.description, arg_usage, self.options = [doc[len('#'):].lstrip().rstrip() for doc in docs]

		# other path special characters can be used in options _and_ in path names
		for invalid in path.SEPARATOR + '|"\'':
			if invalid in self.options:
				raise ValueError("'%s' cannot be an option in program \'%s\'!" % (path.SEPARATOR, self.name))
		all_symbols = [c.isalnum() for c in self.options].count(True) == 0
		if not all_symbols: raise ValueError("Alphanumeric characters are not allowed in options in program '%s'!" % self.name)

		self.usage = '%s%s%s' \
			% (self.name, (' (%s)'%self.options) if self.options else '', (' '+arg_usage) if arg_usage else '')
	def execute(self, args, options, piped, stdin, scope):
		for option in options:
			if option not in self.options: raise OptionException("Invalid option '%s'; %s" % (option, self.usage))

class Program(Runnable):
	"""A native Runnable that uses Python code"""

	def execute(self, args, options, stdin, piped, scope):
		super().execute(args, options, stdin, piped, scope)
		try:
			fn = _compile_program_fn(path.get(self.path, path.File).read())
			return fn(args, options, stdin, piped, scope)
		except ArgumentCountException as e: raise ArgumentCountException(self.usage)
		# TODO: print stacktrace
		except Exception as e:
			if not isinstance(e, (cli.CliException, path.PathException, RunException)):
				print('An error occured during script execution:')
				traceback.print_exc()
			else: raise e

def _compile_program_fn(code):
	def fn(args, options, stdin, piped, scope):
		output = _Logger() if piped else None
		cache = sys.stdout
		if piped: sys.stdout = output
		# whoo! passing the global scope down (``None``) gives the user a lot of power

		custom_scope = dict(globals())
		custom_scope['argv'] = args
		custom_scope['options'] = options
		custom_scope['stdin'] = stdin
		custom_scope['scope'] = scope
		exec(code, custom_scope)
		sys.stdout = cache
		if piped: return str(output).rstrip('\n')
		return None
	return fn
class _Logger():
	def __init__(self):
		self.text = ''
	def write(self, s):
		self.text += s
	def flush(self): pass
	def __str__(self): return self.text

class Script(Runnable):
	"""A primitive sequence of commands that can be run from the terminal, with a few special features"""

	def execute(self, args, options, stdin, scope):	# I think the ``scope`` arg is pretty much irrelevant
		super().execute(args, options, stdin, scope)
		# statements = re.split(r'(?:\\\\)*(?!\\);', path.get(self.path, path.File).read())	# TODO: what if ; is in a string??
		# TODO: change to 'argv' list when/if lists are supported
		# The local scope (varname=>str, value=>str)
		local = EnvironmentDictionary()
		for i,arg in enumerate(args): local['arg%d'%i] = arg
		local['options'] = options
		local['stdin'] = stdin
		cli.process(path.get(self.path, path.File).read(), local)

def find_alias(tokens):
	"""return the syntax of the found alias or ``None``"""

	for syntax in aliases:
		s_statements = cli.tokenize(syntax)
		if len(s_statements) != 1: raise RuntimeError('Either zero or multiple statements in syntax: ' + syntax)#move to prog
		s_tokens = s_statements[0]

		skip = False
		tokens_without_options = list(tokens)
		if len(tokens_without_options) > 1 and cli.is_options(tokens_without_options[1]): tokens_without_options.pop(1)
		if len(tokens_without_options) != len(s_tokens): skip = True	# TODO: account for multiple args?
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
	tokens -- (list)
	return the final command to execute
	"""

	options = tokens.pop(1) if len(tokens) > 1 and cli.is_options(tokens[1]) else None

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
	final_tokens = cli.get_tokens(result)
	if options: final_tokens.insert(1, options)
	return ' '.join(final_tokens)

# HELPER FUNCTIONS (for programs)
def confirm(prompt):
	while True:
		i = input(prompt + ' [y/n] ')
		if i.lower() in ('y', 'n'):
			return i == 'y'
def num(s):
	try:
		return int(s)
	except ValueError:
		try: return float(s)
		except ValueError: pass
	raise ValueError("'%s' is not a number!" % str(s))

def get_program(name):
	for program in programs:
		if program.name == name: return program
	return None

def get_script(name):
	for script in scripts:
		if script.name == name: return script
	return None


class RunException(Exception): pass
# I wish I could have this subclass ValueError, too, because it's a special version of a ValueError
class ArgumentException(RunException): pass
class ArgumentCountException(RunException): pass
class OptionException(RunException): pass
class StdinException(RunException): pass 	# TODO: use this when programs don't support stdin
class NoSuchCommandException(RunException): pass

def _flatten_directory(dir):
	children = []
	for name in dir.children:
		if type(dir.children[name]) is path.Directory:
			children += _flatten_directory(dir.children[name])
		else:
			children.append(dir.children[name])
	return children

def load_session(session):
	# session is useless, because path already defines which session is loaded
	global programs, scripts, aliases

	programs_ = _flatten_directory(path.get('/run/programs'))
	programs = set([
		Program(child) for child in programs_ if type(child) is path.File
	])
	scripts_ = _flatten_directory(path.get('/run/scripts'))
	scripts = set([
		Program(child) for child in scripts_ if type(child) is path.File
	])

	file = open(os.path.join('session', session, 'run.json'))
	aliases = json.load(file)['aliases']
	file.close()

def save_session():
	file = open(os.path.join('session', 'current', 'run.json'), 'w')
	json.dump({'aliases': aliases}, file)
	file.close()

programs = None
scripts = None
aliases = None
