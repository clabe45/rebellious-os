# prints the square root of `num`
# <num>
#

if stdin and len(argv) == 0: argv.append(stdin)
if len(argv) != 1: raise ArgumentCountException()
try:
    base = num(argv[0])
    result = math.sqrt(base)
    print(int(result) if result % 1 == 0 else result)
except ValueError as e:
    raise ArgumentException(e)
