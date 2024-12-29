from restore_sway_layout import swayutil
import os
import random
import sys
import asyncio

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

def random_hex(n):
    return ''.join(['0123456789abcdef'[random.randrange(16)] for i in range(n)])

def print_stderr(msg):
    print(msg, file=sys.stderr)

def get_socket_line(sock):
    result = b''
    disconnected = False
    while True:
        c = sock.recv(1)
        if c == b'\n':
            break
        elif c == b'':
            disconnected = True
            break
        else:
            result += c
    return result, disconnected

async def socket_lines(conn):
    while True:
        l, disconnected = await asyncio.to_thread(lambda: get_socket_line(conn))
        if not (disconnected and l == b''):
            yield l.decode('utf-8')
        if disconnected:
            break

