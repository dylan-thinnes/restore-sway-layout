import subprocess
import ijson
import json
import psutil
from time import sleep
import typing

class SwayTree:
    def __init__(self, internal):
        self.internal: typing.Any = internal

    def workspaces(self):
        for node in self.nodes():
            if node['type'] == 'workspace' and node['name'] != '__i3_scratch':
                yield node

    def nodes(self):
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

        return go(self.internal)

    @staticmethod
    def latest() -> SwayTree:
        raw_existing_tree = swaymsg(['-t', 'get_tree'])
        existing_tree = json.loads(raw_existing_tree.stdout)
        return existing_tree

def swaymsg(args):
    return subprocess.run(['swaymsg'] + args, capture_output=True)

def find_item(target, wait=True, existing_tree=None):
    sway_tree = SwayTree.latest() if existing_tree is None else existing_tree
    for item in sway_tree.nodes():
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
