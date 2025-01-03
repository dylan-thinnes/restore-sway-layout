from restore_sway_layout import swayutil
import os
import random
import sys
import asyncio

def kitty_nodes(sway_tree):
    return {
        node['pid']: node
        for node in swayutil.sway_nodes(sway_tree)
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

def print_stderr(msg):
    print(msg, file=sys.stderr)

# Remove empty trees, flatten 1-trees
def clean_tree(tree):
    if is_leaf(tree):
        return tree

    subtree_count = len(tree['subtrees'])
    if subtree_count == 0:
        return None
    elif subtree_count == 1:
        return clean_tree(tree['subtrees'][0])
    else:
        return {
            'layout': tree['layout'],
            'subtrees': list(map(clean_tree, tree['subtrees']))
        }

# Test for leaf, turn a leaf into a window, make a leaf targeting a window
def is_leaf(tree):
    return tree.get("subtrees") is None

