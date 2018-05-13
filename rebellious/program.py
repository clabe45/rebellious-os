"""Provide a space for programs to be run, so that they must use ``run.*`` notation to access ``run``'s content,
instead of being run _inside_ the module ``run`` itself."""

import sys

import internal
import cli
import env
import path
import run
import user
import session

def compile_fn(code):
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
