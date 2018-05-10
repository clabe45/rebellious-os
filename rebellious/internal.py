import os.path

import cli
import run
import path
import internal
import session

shutting_down = False

# TODO: maybe clean up exception messages

def boot():
	print('*REBELLIOUS OS loading...')
	if os.path.exists(os.path.join('session', 'current')):
		session.load_current()
	else:
		session.load_presets()
	while not shutting_down:
		try: cli.process(cli.get_input())
		except cli.EmptyException: pass
		except cli.SyntaxException as e: print('Syntax error: %s'%str(e))	# TODO: make more specific
		except run.NoSuchCommandException as e: print('*No such command \'%s\'!' % str(e))
		except (run.ArgumentCountException, ValueError) as e: print('*'+str(e))
		except run.ArgumentException as e: print('*'+str(e))
		except run.OptionException as e: print('*'+str(e))
		except run.StdinException as e: print('*This program does not support piping.')
		except path.NotFoundException as e: print('*No such file or directory \'%s\'!' % str(e))
		except path.DuplicateException as e: print('*Duplicate file or directory \'%s\'!' % str(e))
		except path.DirectoryException as e: print('*No such directory \'%s\'!' % str(e))

def shutdown():
	print('*Shutting down...')
	internal.shutting_down = True
	session.save()
