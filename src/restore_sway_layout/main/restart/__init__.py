import json
from restore_sway_layout import vim
from restore_sway_layout import util

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
    for workspace in snapshot['workspaces']:
        for leaf in leaves(workspace):
            print(leaf)
            #if leaf['type'] == 'vim':
            #    vim.restart(leaf['snapshot'])
