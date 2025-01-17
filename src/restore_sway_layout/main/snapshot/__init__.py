from restore_sway_layout import swayutil
from restore_sway_layout import util
from restore_sway_layout import vim
from restore_sway_layout import zsh
from restore_sway_layout import generic
from restore_sway_layout import firefox
from restore_sway_layout import types
from glob import glob
import os
import psutil
import json
import sys
import re
import time
import datetime
import io
import traceback
import typing

def node_to_tree(node: dict, snapshotters: list[tuple[str, types.SupportsSnapshot]]) -> types.Tree:
    workspace_info: types.WorkspaceInfo | None = None
    if node['type'] == 'workspace':
        workspace_info = types.WorkspaceInfo(
            num = node['num'],
            name = node['name']
        )

    if node['layout'] == 'none':
        for name, snapshotter in snapshotters:
            node_snapshot = snapshotter.snapshot(node)
            if node_snapshot is not None:
                return types.Leaf(
                    type = name,
                    snapshot = node_snapshot,
                    workspace = workspace_info
                )

        return types.Leaf(
            type = 'unknown',
            snapshot = node,
            workspace = workspace_info
        )
    else:
        return types.Split(
            layout = node['layout'],
            subtrees = [node_to_tree(node, snapshotters) for node in node['nodes']],
            workspace = workspace_info
        )

def save_snapshot(output_path_or_stream: str | io.IOBase):
    sway_tree = swayutil.SwayTree.latest()
    target_workspaces = list(sway_tree.workspaces())

    snapshotters: list[tuple[str, types.SupportsSnapshot]] = [
        ('vim', vim.Snapshotter(sway_tree)),
        ('zsh', zsh.Snapshotter(sway_tree)),
        ('firefox', firefox),
        ('generic', generic),
    ]

    def make_snapshot() -> types.Snapshot:
        return {
            'timestamp': time.time(),
            'workspaces': [node_to_tree(workspace, snapshotters) for workspace in target_workspaces]
        }

    new_snapshot = make_snapshot()
    if isinstance(output_path_or_stream, io.IOBase):
        json.dump(new_snapshot, fp=output_path_or_stream)
        print(file=output_path_or_stream)
        output_path_or_stream.flush()
    else:
        with open(output_path_or_stream, 'w') as fd:
            json.dump(new_snapshot, fd)

def save_snapshot_without_failure(output_path_or_stream: str | io.IOBase):
    try:
        save_snapshot(output_path_or_stream)
    except Exception as e:
        util.print_stderr('Taking a snapshot failed! Reason:')
        traceback.print_exc()
        pass

def main(args):
    output_path = '/dev/stdout' if args.output == '-' else args.output

    if output_path == '/dev/stdout':
        if isinstance(sys.stdout, io.TextIOWrapper):
            save_snapshot(sys.stdout)
        else:
            util.print_stderr('Could not save snapshot to standard output because standard output has been reconfigured.')
            return 1
    else:
        save_snapshot(output_path)

