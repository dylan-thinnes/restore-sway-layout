from recover import swayutil
import os

def kitty_nodes():
    return {
        node['pid']: node
        for node in swayutil.sway_nodes()
        if node.get('app_id') == 'kitty'
    }

def read_file_to_int(path):
    fd = open(path, 'r')
    i = int(fd.read())
    fd.close()
    return i

def read_file_to_word(path):
    fd = open(path, 'r')
    s = fd.read().strip()
    fd.close()
    return s

def get_display_session_id():
    return read_file_to_word(os.path.join(os.environ['HOME'], '.display-session'))
