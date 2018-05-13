# prints `num1` - `num2`
# <num1> <num2>
#

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise run.ArgumentCountException()
difference = 0
for x,arg in enumerate(argv):
    try:
        n = num(arg)
        difference += n if x == 0 else -n
    except ValueError as e: raise run.ArgumentException(e)
print(difference)
