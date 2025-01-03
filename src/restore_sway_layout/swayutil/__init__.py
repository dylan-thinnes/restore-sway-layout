#!/usr/bin/env python3
import subprocess
import ijson
import json
import psutil
from time import sleep

def sway_workspaces(tree):
    for node in sway_nodes(tree):
        if node['type'] == 'workspace' and node['name'] != '__i3_scratch':
            yield node

def sway_nodes(tree):
    def go(item, workspace=None):
        item['workspace'] = workspace
        yield item
        if item['type'] == 'workspace':
            new_workspace = (item['name'], item.get('num')) # __i3_scratch has no "num" field
        else:
            new_workspace = workspace
        for item in item['nodes']:
            for subitem in go(item, new_workspace):
                yield subitem

    return go(tree)

def sway_get_tree():
    raw_existing_tree = swaymsg(['-t', 'get_tree'])
    existing_tree = json.loads(raw_existing_tree.stdout)
    return existing_tree

def swaymsg(args):
    return subprocess.run(['swaymsg'] + args, capture_output=True)

def find_item(target, wait=True):
    for item in sway_nodes():
        if match_generic(target, item):
            return item

    if wait:
        with subprocess.Popen(['swaymsg', '-m', '-t', 'subscribe', '["window"]'], stdout=subprocess.PIPE) as proc:
            items = ijson.items(proc.stdout, "", multiple_values=True, buf_size=1)

            for item in items:
                if match_generic(target, item['container']):
                    proc.kill()
                    return item['container']

            proc.kill()

    return None

def match_generic(target, node):
    for key, value in dict.items(target):
        if node.get(key) is None:
            return False
        if isinstance(value, dict):
            if not isinstance(node[key], dict):
                return False
            if not match_generic(value, node[key]):
                return False
        else:
             if node[key] != value:
                return False
    return True
