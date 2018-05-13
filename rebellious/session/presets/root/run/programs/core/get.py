# prints the environment variable `var`, exactly like 'echo <`var`>' does
# <var>
# $*

if stdin and len(argv) == 0: argv.append(stdin)
if len(argv) != 1: raise run.ArgumentCountException()
if len(options) == 2: raise run.OptionException("Exclusive options '%s' and '%s'" % options.split(''))

modifier = options
name = argv[0]
print(env.get(name, scope, options))
