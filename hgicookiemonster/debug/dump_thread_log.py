import sys
import traceback

def dump_thread_log(location: str):
    """
    Dump a log of what the threads are currently doing to file.
    :param location: the location of the file to dump log of threads to
    """
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# ThreadID: %s" % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    with open(location, "w+") as logfile:
       logfile.write("\n".join(code))