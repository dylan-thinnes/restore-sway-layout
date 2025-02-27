from restore_sway_layout import swayutil
from restore_sway_layout import types
import os
import random
import sys
import asyncio
import typing
import typing_extensions

def kitty_nodes(sway_tree: swayutil.SwayTree):
    return {
        node['pid']: node
        for node in sway_tree.nodes()
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

def random_hex(n):
    return ''.join(['0123456789abcdef'[random.randrange(16)] for i in range(n)])

def print_stderr(msg: str):
    print(msg, file=sys.stderr)
