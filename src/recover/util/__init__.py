from recover import swayutil
import os

def kitty_nodes():
    return {
        node['pid']: node
        for node in swayutil.sway_nodes()
        if node.get('app_id') == 'kitty'
    }

def read_file_to_int(path):
    return read_file_to_f(path, int)

def read_file_to_word(path):
    return read_file_to_f(path, lambda x: x)

def read_file_to_f(path, f):
    exc = None
    for attempt in range(10):
        try:
            with open(path, 'r') as fd:
                s = f(fd.read().strip())
                break
        except ValueError as ex:
            exc = ex
    if exc is not None:
        raise exc
    return s

def get_display_session_id():
    return read_file_to_word(os.path.join(os.environ['HOME'], '.display-session'))
