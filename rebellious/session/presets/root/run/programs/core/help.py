# prints the help for `command` or lists all commands
# [command]
#

if stdin: raise StdinException()
if len(argv) > 1: raise ArgumentCountException()
if len(argv) == 0: print('\t'.join([program.name for program in programs]))
else:
    name = argv[0]
    program = get_program(name) # TODO: allow user to use run.get_program somehow?
    if program: print('%s - %s' % (program.usage, program.description))
    else: print('No such program \'%s\'' % name)
