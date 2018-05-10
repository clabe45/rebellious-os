# tests if `num1` is greater than `num2`
# <num1> <num2>
#

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise ArgumentException()
try:
    print(str(num(argv[0]) > num(argv[1])).lower())
except ValueError as e:
    raise ArgumentException(e)
