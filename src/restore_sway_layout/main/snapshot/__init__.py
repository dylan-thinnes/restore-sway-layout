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

def save_snapshot(output_path, output_stream=None, workspace_filter=None):
    sway_tree = swayutil.sway_get_tree()
    if workspace_filter is not None and len(workspace_filter) > 0:
        target_workspaces = [
            workspace
            for workspace in swayutil.sway_workspaces(sway_tree)
            if workspace["num"] in workspace_filter
        ]
    else:
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

    if output_stream is not None:
        json.dump(make_snapshot(), output_stream)
        print(file=output_stream)
        output_stream.flush()
    else:
        with open(output_path, 'w') as fd:
            json.dump(make_snapshot(), fd)

def main(args):
    output_path = '/dev/stdout' if args.output == '-' else args.output

    is_stdout = args.output == '-' or args.output == '/dev/stdout'
    if is_stdout:
        output_stream = sys.stdout
    elif args.append:
        output_stream = open(output_path, 'w+')
    else:
        output_stream = None

    if args.watch is None:
        save_snapshot(output_path, output_stream, args.workspace)
    else:
        n = 0
        while True:
            util.print_stderr(f'Saving snapshot #{n} at {datetime.datetime.now()}')
            save_snapshot(output_path, output_stream, args.workspace)
            n += 1
            time.sleep(args.watch)
