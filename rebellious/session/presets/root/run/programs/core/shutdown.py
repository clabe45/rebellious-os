# exits the current session
#
#

if len(argv) > 0: raise run.ArgumentCountException()
internal.shutdown()
