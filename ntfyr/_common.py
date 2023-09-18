
import logging
import sys


logging.basicConfig(format='%(levelname)s:%(name)s: %(message)s',
                    stream=sys.stderr)
log = logging.getLogger(name='ntfyr')
log.setLevel(logging.ERROR)
