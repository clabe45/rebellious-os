# sets the environment variable `var` to `value`, or deletes if no `value` is provided
# <var> [value]
# $

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) < 1: raise ArgumentCountException()
global_ = '$' in options
name = argv[0]

sc = env.variables if global_ else scope
if len(argv) == 2:
    value = argv[1]
    try:
        sc[name] = value
    except ValueError as e:
        raise ArgumentException(e)
elif name in sc: del sc[name]
