import json
from restore_sway_layout import vim
from restore_sway_layout import zsh
from restore_sway_layout import firefox
from restore_sway_layout import util
from restore_sway_layout import swayutil
from restore_sway_layout import types

def leaves(tree):
    if util.is_leaf(tree):
        yield tree
    else:
        for subtree in tree['subtrees']:
            for leaf in leaves(subtree):
                yield leaf

def main(args):
    snapshot = json.load(args.snapshot)
    snapshot = util.clean_tree(snapshot)
    sway_tree = swayutil.SwayTree.latest()
    restarters: list[tuple[str, types.SupportsRestart]] = [
        ('vim', vim.Restarter(sway_tree)),
        ('zsh', zsh.Restarter(sway_tree)),
        ('firefox', firefox.Restarter()),
    ]
    for workspace in snapshot['workspaces']:
        for leaf in leaves(workspace):
            for name, restarter in restarters:
                restarter_thunk = restarter.restart(leaf['type'], leaf['snapshot'])
                if restarter_thunk is not None:
                    util.print_stderr(f'Found restarter for snapshot {leaf}: {restarter}')
                    util.print_stderr(f'Running restarter...')
                    restarter_thunk()
