#!/usr/bin/env python3
from recover import swayutil
from recover import vim
from recover import zsh
from recover import generic
from recover import firefox
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

def node_to_tree(node):
    result = {}

    if node['type'] == 'workspace':
        result['workspace_num'] = node['num']
        result['workspace_name'] = node['name']

    if node['layout'] == 'none':
        vim_snapshot = vim.snapshot(node)
        zsh_snapshot = zsh.snapshot(node)
        generic_snapshot = generic.snapshot(node)
        firefox_snapshot = firefox.snapshot(node)
        if vim_snapshot is not None:
            result['type'] = 'vim'
            result['snapshot'] = vim_snapshot
        elif zsh_snapshot is not None:
            result['type'] = 'zsh'
            result['snapshot'] = zsh_snapshot
        elif firefox_snapshot is not None:
            result['type'] = 'firefox'
            result['snapshot'] = firefox_snapshot
        elif generic_snapshot is not None:
            # Default to populating the title and app_id
            result['type'] = 'generic'
            result['snapshot'] = generic_snapshot
        else:
            result['type'] = 'unknown'
            result['snapshot'] = node
    else:
        result['layout'] = node['layout']
        result['subtrees'] = list(map(node_to_tree, node['nodes']))

    return result

def main(args):
    output_path = '/dev/stdout' if args.output == '-' else args.output
    if not os.path.exists(output_path):
        print(f'Output path {output_path} does not exist!', file=sys.stderr)
        return

    is_stdout = args.output == '-' or args.output == '/dev/stdout'
    if is_stdout:
        output_stream = sys.stdout
    elif args.append:
        output_stream = open(output_path, 'w+')
    else:
        output_stream = None

    def take_snapshot():
        nonlocal output_stream
        if len(args.workspace) > 0:
            target_workspaces = [
                workspace
                for workspace in swayutil.sway_workspaces()
                if workspace["num"] in args.workspace
            ]
        else:
            target_workspaces = list(swayutil.sway_workspaces())

        if output_stream is not None:
            json.dump(list(map(node_to_tree, target_workspaces)), output_stream)
            print(file=output_stream)
            output_stream.flush()
        else:
            with open(output_path, 'w') as fd:
                json.dump(list(map(node_to_tree, target_workspaces)), fd)

    if args.watch is None:
        take_snapshot()
    else:
        n = 0
        while True:
            print(f'Saving snapshot #{n} at {datetime.datetime.now()}', file=sys.stderr)
            take_snapshot()
            n += 1
            time.sleep(args.watch)
