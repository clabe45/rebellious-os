# prints `num1` * `num2`
# <num1> <num2>
#

if stdin and len(argv) == 1: argv.append(stdin)
if len(argv) != 2: raise ArgumentCountException()
product = 1
for arg in argv:
    try:
        product *= num(arg) # TODO: test if it keeps ints as ints
    except ValueError as e: raise ArgumentException(e)
print(product)
