import ijson
import sys
import subprocess
import random
import tempfile
import json

from restore_sway_layout import swayutil
from restore_sway_layout import util

#class Mock:
#    def __getattr__(self, name):
#        def p(*args, **kwargs):
#            print(name, *args, kwargs)
#        return p
#swayutil = Mock()

def make_random_window(tree, prompt, keep_prompt):
    self_title = "capture-{:020d}".format(random.randint(0, 9999999999999999999))

    info_fileno, info_path = tempfile.mkstemp()
    info_fd = open(info_path, "w")
    json.dump({
        'snapshot': tree['snapshot'],
        'type': tree['type'],
        'self_title': self_title,
    }, info_fd)
    info_fd.close()

    swayutil.swaymsg([f'exec', f'foot -a capture -T {self_title} {sys.executable} -m restore_sway_layout.main.relocate_one "{info_path}" {1 if prompt else 0} {1 if keep_prompt else 0}'])
    #swayutil.swaymsg([f'exec', f'foot -a capture -T {self_title} --hold echo "{info_path}"'])
    return swayutil.find_item({
        'app_id': 'capture',
        'name': self_title,
    })

# Build a tree of windows in the specified layout
def build_tree(tree, prompt, keep_prompt):
    if util.is_leaf(tree):
        build_leaf(tree, prompt, keep_prompt)
    else:
        build_tree(tree['subtrees'][0], prompt, keep_prompt)
        swayutil.swaymsg(['splitv'])
        for subtree in tree['subtrees'][1:]:
            build_tree(subtree, prompt, keep_prompt)
        swayutil.swaymsg([f'layout {tree["layout"]}'])
        swayutil.swaymsg(['focus parent'])

def build_leaf(tree, prompt, keep_prompt):
    return make_random_window(tree, prompt, keep_prompt)

# Set a workspace to contain a tree
def set_workspace(num, name, tree, prompt, keep_prompt):
    swayutil.swaymsg([f'workspace {num}'])
    swayutil.swaymsg([f'rename workspace {num} to "{name}"'])
    build_tree(util.clean_tree(tree), prompt, keep_prompt)

def build_snapshot(snapshot, prompt, keep_prompt):
    for workspace in snapshot['workspaces']:
        set_workspace(workspace['workspace_num'], workspace['workspace_name'], workspace, prompt, keep_prompt)

def main(args):
    build_snapshot(json.load(args.snapshot), args.prompt, args.keep_prompt)
