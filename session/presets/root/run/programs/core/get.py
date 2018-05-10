# prints the environment variable `var`, exactly like 'echo <`var`>' does
# <var>
# $

if stdin and len(argv) == 0: argv.append(stdin)
if len(argv) != 1: raise ArgumentCountException()
global_ = '$' in options
name = argv[0]
print(env.get(name, scope if not global_ else None))
