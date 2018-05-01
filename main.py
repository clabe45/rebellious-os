"""
You guess what it is :>
"""
# TODO: LOOK FOR CROSS-REFERNCING (OKAY IN PYTHON?) for files
print('*Starting...')

import cli
import run
import path
import internal

def boot():
	while not internal.shutting_down:
		i = input('%s > ' % str(path.cwd))
		try: cli.process(i)
		except cli.EmptyException: pass
		except cli.SyntaxException as e: print('Syntax error: %s'%str(e))	# TODO: make more specific
		except run.NoSuchProgramException as e: print('*Invalid program \'%s\'!' % str(e))
		except (run.ArgumentCountException, ValueError) as e: print('*'+str(e))
		except run.ArgumentException as e: print('*'+str(e))
		except run.OptionException as e: print('*'+str(e))
		except path.NotFoundException as e: print('*No such file or directory \'%s\'!' % str(e))
		except path.DuplicateException as e: print('*Duplicate file or directory \'%s\'!' % str(e))
		except path.DirectoryException as e: print('*No such directory \'%s\'!' % str(e))

boot()
