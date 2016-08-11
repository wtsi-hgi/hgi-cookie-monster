import atexit
import os
from datetime import datetime

# TODO? It might be better to use Python's logging module to do this,
# but it seems to be very awkward to create a separate logger that logs
# to a file... I can't be bothered for the sake of this, so I just fall
# back to run-of-the-mill FS operations.
import logging

_LOG_FORMAT = "{timestamp}\t{message}\n"

class RuleOutputWriter:
    """
    Simple log file writer
    """
    def __init__(self, filename:str):
        filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        logging.debug('Writing rule output to "%s"', filename)

        try:
            self.file = open(filename, 'a', 1)
        except FileNotFoundError:
            self.file = open(filename, 'w', 1)

        atexit.register(self.file.close)

    def __call__(self, message:str):
        ts = datetime.utcnow()
        log_data = {
            'timestamp': '{:%Y-%m-%d %H:%M:%S}'.format(ts),
            'message':   message
        }

        self.file.write(_LOG_FORMAT.format(**log_data))
