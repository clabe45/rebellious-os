import re

import path
import run
import env

def tokenize(i):
	"""Breaks up the input into tokens separated by spaces. Spaces can be escaped by surrounding them in quotes.
	Very primitive, but... no RE!!"""

	# ugh
	tokens = []
	quotes_opened, raw, escaped, curr_token = None, False, False, None
	for x,c in enumerate(i):
		if c == '\\' and not escaped:
			escaped = True
			continue
		elif c == 'r' and (x < len(i)-1 and i[x+1] in ('"', "'")):
			raw = True
			continue
		elif not escaped:
			if c in ("'", '"'):
				if not quotes_opened:
					# start token
					curr_token = ''
					quotes_opened = c
				elif quotes_opened == c:
					quotes_opened = None
					raw = False
		else: escaped = False
		#elif c == ' ' and not quotes_opened:
		if c == ' ' and not quotes_opened:
			# end token
			if not curr_token is None: tokens.append(curr_token)
			curr_token = None
			raw = False
		else:
			if curr_token is None: curr_token = ''
			if raw and c in ('\\<>'): curr_token += '\\'
			curr_token += c
	if not curr_token is None:
		tokens.append(curr_token)
		curr_token = None
	if quotes_opened: raise SyntaxException('open quotes at EOL')
	return tokens

def process(i, scope=env.variables, _piped_input=None):
	"""Runs ``i`` as if it were typed into the terminal

	scope -- (dict) the local scope of a script, if relevant
	_piped_input -- (str) <em>not to be used outside of recursion;</em> the rest of the command when piping
	"""

	i = re.sub(' +', ' ', i)
	tokens = tokenize(i)

	pipe_idx = None
	try:
		pipe_idx = tokens.index('|')
	except ValueError: pass

	if len(tokens) == 0: raise EmptyException()
	command_name = tokens[0]		# first (primary) command name, or only if not chaining; can be a PATH

	args = tokens[1 : pipe_idx if pipe_idx else len(tokens)] if len(tokens) > 1 else []
	# similar to -abc, but instead _+: ; so, it has to be all symbolic (non alpha-numeric)
	options = ''
	if len(args) > 0:
		all_symbols = [c.isalnum() for c in args[0]].count(True) == 0
		if all_symbols and not (path.SEPARATOR in args[0] or '.' in args[0]):
			options = args[0]
			args.pop(0)
	for x,arg in enumerate(args):
		escaped = r'(?:\\\\)*(?!\\)'	# preceded by anything but an even number of \'s (I think that's it)
		# TODO: exclude certain characters from varname
		expr = r'((?:{}\$<)|(?:{}<))([^<>\\]+(?:\\\\)*)(?!\\)>'.format(escaped, escaped, escaped)	# matches $<varname> or <varname>;
		m = re.search(expr, arg)
		while m:
			global_ = m.group(1).endswith('$<')	# whether first option was chosen in | alternative
			start,end = m.span(2)
			start -= len('$<') if global_ else len('<')
			end += len('>')
			name = m.group(2)

			sc = env.variables if (global_ or not scope) else scope
			value = sc[name] if name in sc else '{undefined}'	# TODO: maybe change to '{unset}'
			arg = arg[:start] + value + arg[end:]
			m = re.search(expr, arg)
		args[x] = re.sub(r'\\(.)', lambda match: match.group(1), arg)

	if _piped_input: args.append(_piped_input)

	args = [arg[1:-1] if arg[0] in ("'", '"') and arg[-1]==arg[0] else arg for arg in args]
	for p in run.programs:
		if p.name == command_name:
			try: output = p.execute(args, options, scope)
			except ValueError as e: print(str(e))

			if pipe_idx:
				rest_of_chain = tokens[pipe_idx+1:]
				process(' '.join(rest_of_chain), scope, output)
			elif not output is None:
				print(output)
			break
		syntax = run.find_alias(tokens)
		if syntax:
			process(run.fill_alias(syntax, tokens))
			break
	else:
		for script in run.scripts:
			if script.name == command_name:
				script.execute(args, options, scope)
				break
		else: raise run.NoSuchCommandException(command_name)

class CliException(Exception): pass
class EmptyException(CliException): pass
class SyntaxException(CliException): pass	# note: distinct from SyntaxError
