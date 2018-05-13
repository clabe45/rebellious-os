# prints `num1` / `num2`
# <num1> <num2>
#

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise run.ArgumentCountException()
quotient = 1
for x,arg in enumerate(argv):
    try:
        n = num(arg)
        quotient *= n if x == 0 else 1/n
    except ValueError as e: raise run.ArgumentException(e)
    except ZeroDivisionError: raise run.ArgumentException('Cannot / by 0!')
print(quotient)
