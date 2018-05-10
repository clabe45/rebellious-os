# performs an action of the system alias map
# <get/set/clear/list> [syntax] [alias]
#

if stdin: raise StdinException()
if len(argv) < 1: raise ArgumentCountException()
subcommand = argv[0]
syntax = argv[1] if len(argv) > 1 else None
if syntax: cli.get_tokens(syntax)  # ensure that it's one statement (it will raise an error otherwise)

if subcommand == 'set':
    if len(argv) != 3: raise ArgumentCountException()
    alias = argv[2]
    cli.get_tokens(alias)
    aliases[syntax] = alias
    print("Syntax '%s' bound to '%s'" % (syntax, alias))

elif subcommand == 'get':
    if len(argv) != 2: raise ArgumentCountException()
    alias = aliases[syntax]
    print("%s => %s" % (syntax, alias))

elif subcommand == 'clear':
    if len(argv) != 2: raise ArgumentCountException()
    if confirm('Remove alias \'%s\'?' % syntax):
        del aliases[syntax]
        print("Syntax '" + syntax + "' removed")

elif subcommand == 'list':
    if len(argv) != 1: raise ArgumentCountException()
    ls = ["%s => %s" % (syntax, aliases[syntax]) for syntax in aliases]
    ls.sort()
    print('\n'.join(ls))
else: raise ArgumentException("No such alias function '%s'" % subcommand)
