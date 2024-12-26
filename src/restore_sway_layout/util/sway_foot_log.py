import io
import sys
import random
from restore_sway_layout import swayutil
import tempfile

class SwayFootLog(io.IOBase):
    def __init__(self):
        self.title = "sway-foot-log-{:020d}".format(random.randint(0, 9999999999999999999))
        (self.fileno, self.filepath) = tempfile.mkstemp()
        swayutil.swaymsg(['exec', f'foot -a capture -T {self.title} tail -f {self.filepath}'])
        swayutil.find_item({'name': self.title})
        self.fd = open(self.filepath, 'a')

    # Override default implementation to say this log is writeable
    def writeable(self):
        return True

    # `read` is not provided by IOBase, have to stub it out ourselves
    def read(self, *args, **kwargs):
        raise io.UnsupportedOperation('read')

    def write(self, msg):
        self.fd.write(msg)
        self.fd.flush()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print('Exit called...')
        swayutil.swaymsg([f'[title="^{self.title}$"] kill'])
        self.fd.close()
        return False

#with SwayFootLog() as log:
#    print('Hello!', file=log)
#    raise ValueError('hello')
#    sys.stdin.readline()

#with TkLog() as log:
#    print('Hi!', file=log)
#    sys.stdin.readline()
#    raise ValueError('hello')
#    sys.stdin.readline()
