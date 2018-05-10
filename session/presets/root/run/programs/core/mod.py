# prints `num1` modulo `num2`
# <num1> <num2>
#

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise ArgumentException()
try:
    dividend, divisor = [num(arg) for arg in argv]
    print(dividend % divisor)
except ValueError as e: raise ArgumentException(e)
except ZeroDivisionError: raise ArgumentException('Cannot / by 0!')
