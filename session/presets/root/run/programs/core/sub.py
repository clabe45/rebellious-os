# prints `num1` - `num2`
# <num1> <num2>
#

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise ArgumentCountException()
difference = 0
for x,arg in enumerate(argv):
    try:
        n = num(arg)
        difference += n if x == 0 else -n
    except ValueError as e: raise ArgumentException(e)
print(difference)
