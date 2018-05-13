# reads from stdin and prints result
# [prompt]
#
if stdin and len(argv) == 0: argv.append(stdin)
if len(argv) > 1: raise run.ArgumentCountException()
prompt = argv[0] if len(argv) == 1 else None

if prompt: print(input(prompt))
else: print(input())
