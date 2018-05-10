# prints `num1` ^ `num2`
# <num1> <num2>
#

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise ArgumentCountException()
try:
    base, power = [num(arg) for arg in argv]
    result = base**power
    print(int(result) if result % 1 == 0 else result)
except ValueError as e:
    raise ArgumentException(e)
