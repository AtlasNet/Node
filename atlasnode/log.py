import logging
import sys
from datetime import datetime


class ConsoleHandler (logging.StreamHandler):
    def __init__(self, stream):
        #self.debug = debug
        logging.StreamHandler.__init__(self, stream)

    def handle(self, record):
        if not self.stream.isatty():
            return logging.StreamHandler.handle(self, record)

        s = ''
        d = datetime.fromtimestamp(record.created)
        s += d.strftime("\033[37m%d.%m.%Y %H:%M \033[0m")
        #if self.debug:
        #    s += ('%s:%s' % (record.filename, record.lineno)).ljust(30)
        l = ''
        if record.levelname == 'DEBUG':
            l = '\033[37mDEBUG\033[0m '
        if record.levelname == 'INFO':
            l = '\033[32mINFO\033[0m  '
        if record.levelname == 'WARNING':
            l = '\033[33mWARN\033[0m  '
        if record.levelname == 'ERROR':
            l = '\033[31mERROR\033[0m '
        s += l.ljust(9)
        try:
            s += record.msg % record.args
        except:
            s += record.msg
        s += '\n'
        self.stream.write(s)


def init(level=logging.INFO):
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    stdout = ConsoleHandler(sys.stdout)
    stdout.setLevel(level)
    log.addHandler(stdout)
    return log
