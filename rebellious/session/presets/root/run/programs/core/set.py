# sets the environment variable `var` to `value`, or deletes if no `value` is provided
# <var> [value]
# $*

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) < 1: raise ArgumentCountException()
if len(options) == 2: raise OptionException("Excludive options '%s' and '%s'" % options.split(''))

modifier = options
name = argv[0]
if len(argv) == 2:
    value = argv[1]
    try:
        env.set(name, value, scope, modifier)
    except ValueError as e:
        raise ArgumentException(e)
else:
    try:
        env.remove(name, scope, modifier)
    except KeyError: pass
