# clears the screen
#
#

if len(argv) > 0: raise run.ArgumentCountException()
os.system('cls' if os.name == 'nt' else 'clear')	# taken from https://stackoverflow.com/a/2084628/3783155
print()	# empty line
