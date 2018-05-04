"""
You guess what it is :>
"""
# TODO: create ``format(s)`` function that precedes single quotes with backslashes and surrounds ``s`` with single quotes
print('*REBELLIOUS OS loading...')

import cli
import run
import path
import internal

def boot():
	while not internal.shutting_down:
		try: cli.process(cli.get_input())
		except cli.EmptyException: pass
		except cli.SyntaxException as e: print('Syntax error: %s'%str(e))	# TODO: make more specific
		except run.NoSuchCommandException as e: print('*No such command \'%s\'!' % str(e))
		except (run.ArgumentCountException, ValueError) as e: print('*'+str(e))
		except run.ArgumentException as e: print('*'+str(e))
		except run.OptionException as e: print('*'+str(e))
		except path.NotFoundException as e: print('*No such file or directory \'%s\'!' % str(e))
		except path.DuplicateException as e: print('*Duplicate file or directory \'%s\'!' % str(e))
		except path.DirectoryException as e: print('*No such directory \'%s\'!' % str(e))

boot()
