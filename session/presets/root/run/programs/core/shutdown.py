# exits the current session
#
#

if len(argv) > 0: raise ArgumentCountException()
internal.shutdown()
