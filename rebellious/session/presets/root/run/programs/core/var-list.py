# lists the variables of the given scope or the global scope
#
# $*

def format_env_dict(d):
    # TODO: prettify
    return '\n'.join(["%s: %s" % (key, d[key]) for key in d])

if stdin and len(argv) == 0: argv.append(stdin)
if len(argv) > 1: raise run.ArgumentCountException()
if len(options) == 2: raise run.OptionException("Exclusive options '%s' and '%s'" % options.split(''))

modifier = options
result = env.list(scope, modifier)

if type(result) in (env.EnvironmentDictionary, dict):
    print(format_env_dict(result))
else:
    variables, constants = result
    print('--Variables:')
    print(format_env_dict(variables))
    print('--Constants:')
    print(format_env_dict(constants))
