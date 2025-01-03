#!/usr/bin/env python3
from restore_sway_layout import swayutil
from restore_sway_layout import util
from restore_sway_layout import vim
from restore_sway_layout import zsh
from restore_sway_layout import generic
from restore_sway_layout import firefox
from glob import glob
import os
import psutil
import json
import sys
import re
import time
import datetime
import io

def mk_leaf(target_title, app_id):
    return { 'title': target_title, 'app_id': app_id }

def node_to_tree(node, snapshotters, sway_tree):
    result = {}

    if node['type'] == 'workspace':
        result['workspace_num'] = node['num']
        result['workspace_name'] = node['name']

    if node['layout'] == 'none':
        result['type'] = 'unknown'
        result['snapshot'] = node
        for name, snapshotter in snapshotters:
            node_snapshot = snapshotter.snapshot(node)
            if node_snapshot is not None:
                result['type'] = name
                result['snapshot'] = node_snapshot
                break
    else:
        result['layout'] = node['layout']
        result['subtrees'] = [node_to_tree(node, snapshotters, sway_tree) for node in node['nodes']]

    return result

def save_snapshot(output_path_or_stream):
    sway_tree = swayutil.sway_get_tree()
    target_workspaces = list(swayutil.sway_workspaces(sway_tree))

    snapshotters = [
        ('vim', vim.Snapshotter(sway_tree)),
        ('zsh', zsh.Snapshotter(sway_tree)),
        ('firefox', firefox),
        ('generic', generic),
    ]

    def make_snapshot():
        return {
            'timestamp': time.time(),
            'workspaces': [node_to_tree(workspace, snapshotters, sway_tree) for workspace in target_workspaces]
        }

    if isinstance(output_path_or_stream, io.IOBase):
        json.dump(make_snapshot(), output_path_or_stream)
        print(file=output_path_or_stream)
        output_path_or_stream.flush()
    else:
        with open(output_path_or_stream, 'w') as fd:
            json.dump(make_snapshot(), fd)

def main(args):
    output_path = '/dev/stdout' if args.output == '-' else args.output

    if output_path == '/dev/stdout':
        save_snapshot(sys.stdout)
    else:
        save_snapshot(output_path)

