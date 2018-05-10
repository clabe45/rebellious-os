# prints `num1` / `num2`
# <num1> <num2>
#

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise ArgumentCountException()
quotient = 1
for x,arg in enumerate(argv):
    try:
        n = num(arg)
        quotient *= n if x == 0 else 1/n
    except ValueError as e: raise ArgumentException(e)
    except ZeroDivisionError: raise ArgumentException('Cannot / by 0!')
print(quotient)
