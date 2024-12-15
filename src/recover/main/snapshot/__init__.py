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
    numeric_args = [
        int(string)
        for string in args.workspace
        if re.fullmatch('[0-9]+', string)
    ]

    if len(numeric_args) > 0:
        target_workspaces = [
            workspace
            for workspace in swayutil.sway_workspaces()
            if workspace["num"] in numeric_args
        ]
    else:
        target_workspaces = list(swayutil.sway_workspaces())

    workspace_report = ", ".join(map(lambda w: str(w['num']), target_workspaces))
    print(f"Workspaces: {workspace_report}", file=sys.stderr)

    json.dump(list(map(node_to_tree, target_workspaces)), args.output)
