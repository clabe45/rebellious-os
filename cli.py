import re

import path
import run
import env

# TODO: consider making nonexistent variable references <foo> output itself <foo>, other than {undefined}

def get_input():
	"""Read input, accounting for the multiline character r'\', and return concatenated result
	(excluding the mulitline characters at the end of each line)
	"""

	prompt, i = '%s > ' % str(path.cwd), ''
	while True:
		ln = input(prompt)
		# check if ln ends with multiline character; but, since it's the escape character, don't match \\
		if not re.search(r'^[^#]+(?<!\\)(?:\\\\)*\\$', ln):
			i += ln
			break
		i += ln[:-1] + '\n'
		prompt = '... '
	return i

# MAKE TOKENIZE INCLUDE BACKSLASHES FOR ESCAPING
def tokenize(i):
	"""Break up the input into *two levels of tokenization*:
	 - statements
	 - and within each statement, tokens

	Statements are separated by semicolons.
	Tokens are separated by one or more spaces. Spaces can be escaped by surrounding them in quotes.
	Anything between a '#' and a newline or EOL are ignored as comments.
	Very primitive, but... no RE!!
	i -- zero or more statements in text form (str)
	"""

	# this is awful
	statements = [[]]	# empty 2D array of statements and then tokens
	quotes_opened, raw, escaped, commented, curr_token = None, False, False, False, None
	for x,c in enumerate(i):
		next = i[x+1] if x+1<len(i) else None
		if c == '\\' and not (raw or escaped) and (next and next in '\\#'):
			escaped = True	# ``escaped`` is only relevant to tokenizing functionality
			continue
		elif c == 'r' and next in ('"', "'"):
			raw = True
			continue
		elif not escaped:
			if not raw and not quotes_opened and c == '#':
				commented = True
			if c in ("'", '"'):	# the quotes have nothing to do with being raw or not
				if not quotes_opened:
					# start token
					curr_token = ''
					quotes_opened = c
				elif quotes_opened == c:
					quotes_opened = None
					raw = False
		else: escaped = False

		if not commented:
			if not quotes_opened and c in ' \t;':
				# either way, end token
				if not curr_token is None:
					tokens = statements[-1]
					tokens.append(curr_token)
				curr_token = None
				raw = False
				# now, start a new statement if necessary
				if c == ';':
					# end statement
					statements.append([])	# new list of tokens
			else:
				if curr_token is None: curr_token = ''
				if raw and c in '\\#<>': curr_token += '\\'
				curr_token += c

	if not curr_token is None:
		tokens = statements[-1]
		tokens.append(curr_token)
		curr_token = None
	if quotes_opened: raise SyntaxException('open quotes at EOF!')
	return statements

def get_tokens(i):
	"""Return the first statement in ``tokenize(i)`` or raise an error if zero or more than one statements"""

	statements = tokenize(i)
	if len(statements) != 1: raise ValueError('Either zero or multiple statements in \'%s\'!' % i)
	return statements[0]

def process(i, scope=None):
	"""Run ``i`` as if it were typed into the terminal

	scope -- (dict) the local scope of a script, if relevant
	"""

	if scope is None: scope = env.variables

	i = re.sub(' +', ' ', i)
	statements = tokenize(i)
	for statement in statements:
		process_statement(statement, scope)

def process_statement(tokens, scope=None, _piped_input=None):
	# weird happening: when I use ^ scope=env.variables, it assigns None to scope, even though env.variables has been inited
	# this is because it was initiated in a function (yes, using the global keyword), but it's strange behavior
	# (SO it when I get internet, self)
	"""Run the single processed statement ``tokens`` as a list of tokens

	tokens -- the statement (str)
	scope -- the local scope of a script, if relevant (dict)
	_piped_input -- (str) *not to be used outside of recursion;* for chaining (stdout->stdin)
	"""

	if scope is None: scope = env.variables

	pipe_idx = None
	try: pipe_idx = tokens.index('|')
	except ValueError: pass

	if len(tokens) == 0: raise EmptyException()
	command_name = tokens[0]		# first (primary) command name, or only if not chaining; can be a PATH

	args = tokens[1 : pipe_idx if pipe_idx else len(tokens)] if len(tokens) > 1 else []
	# similar to -abc, but instead _+: ; so, it has to be all symbolic (non alpha-numeric)
	options = ''
	if len(args) > 0:
		if is_options(args[0]):
			options = args[0]
			args.pop(0)
	for x,arg in enumerate(args): args[x] = _use_special_characters(arg, scope)

	if not _piped_input: _piped_input = ''
	args = [arg[1:-1] if arg[0] in ("'", '"') and arg[-1]==arg[0] else arg for arg in args]
	for c in list(run.programs) + list(run.scripts):	# TODO: works?
		if c.name == command_name:
			output = c.execute(args, options, _piped_input, not pipe_idx is None, scope)
			# except ValueError as e: print(str(e))

			if pipe_idx:
				rest_of_chain = tokens[pipe_idx+1:]
				tokens = get_tokens(' '.join(rest_of_chain))
				process_statement(tokens, scope, output)
			elif not output is None:
				print(output)
			break
		syntax = run.find_alias(tokens)
		if syntax:
			tokens = get_tokens(run.fill_alias(syntax, tokens))
			process_statement(tokens, scope, _piped_input)
			break
	else: raise run.NoSuchCommandException(command_name)

def is_options(token):
	all_symbols = [c.isalnum() for c in token].count(True) == 0
	contains_path_chars = path.SEPARATOR in token 	# other path characters aren't reserved, so they can be used in both cases
	contains_cli_chars = '|' in token
	is_quoted = token[0] in ("'", '"') and token[0] == token[-1]
	return all_symbols and not (contains_path_chars or contains_cli_chars or is_quoted)

def _use_special_characters(s, scope):
	s = _replace_vars(s, scope)
	def unescape(m):
		# remove the backslash only if the 2nd captured group is "escapable", or a valid character to be escaped
		return m.group(1) if m.group(1) in '<>' else m.group(0)

	# keep backslash if it doesn't escape a valid character
	return re.sub(r'\\(.)', unescape, s)

def _replace_vars(s, scope):
	"""Substitutes variable (and constant) names for their respective values. Note that escaped characters are ignored"""

	expr = r'(\$)?(?<!\\)(?:\\\\)*<([^<>\\]+(?<!\\)(?:\\\\)*)>'	# matches $<varname> or <varname>
	m = re.search(expr, s)
	while m:
		local = bool(m.group(1))	# whether first option was chosen in | alternative
		start,end = m.span(2)
		start -= len('$<') if local else len('<')
		end += len('>')
		name = m.group(2)

		# output name if it's not a valid variable name
		# escape < and > to prevenet infinite regex loop
		value = env.get(name, scope if local else None) if env.validate_name(name) else '\<%s\>'%name
		s = s[:start] + value + s[end:]
		m = re.search(expr, s)
	return s

class CliException(Exception): pass
class EmptyException(CliException): pass
class SyntaxException(CliException): pass	# note: distinct from SyntaxError
