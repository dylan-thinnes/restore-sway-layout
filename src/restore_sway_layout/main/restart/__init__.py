import json
from restore_sway_layout import vim
from restore_sway_layout import util
from restore_sway_layout import swayutil

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
    sway_tree = swayutil.sway_get_tree()
    restarters = [
        ('vim', vim.Restarter(sway_tree))
    ]
    for workspace in snapshot['workspaces']:
        for leaf in leaves(workspace):
            for name, restarter in restarters:
                result = restarter.restart(leaf['type'], leaf['snapshot'])
                if result is not None:
                    util.print_stderr(name, result)
                    result()
