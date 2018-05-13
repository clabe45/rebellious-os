# prints the `root` root of `base`
# <root> <base>
#

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise run.ArgumentCountException()
try:
    root, base = [num(arg) for arg in argv]
    result = base**(1/root)
    print(int(result) if result % 1 == 0 else result)
except ValueError as e:
    raise run.ArgumentException(e)
