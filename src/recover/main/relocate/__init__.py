#!/usr/bin/env python3
import ijson
import sys
import subprocess
import random
import tempfile
import json

from recover import swayutil

#class Mock:
#    def __getattr__(self, name):
#        def p(*args, **kwargs):
#            print(name, *args, kwargs)
#        return p
#swayutil = Mock()

def make_random_window(tree, prompt, keep_prompt):
    self_title = "capture-{:020d}".format(random.randint(0, 9999999999999999999))

    info_path = f"/tmp/{self_title}"
    info_fd = open(info_path, "w")
    json.dump({
        'snapshot': tree['snapshot'],
        'type': tree['type'],
        'self_title': self_title,
    }, info_fd)
    info_fd.close()

    swayutil.swaymsg([f'exec', f'foot -a capture -T {self_title} python3 -m recover.main.relocate_one "{info_path}" {1 if prompt else 0} {1 if keep_prompt else 0}'])
    #swayutil.swaymsg([f'exec', f'foot -a capture -T {self_title} --hold echo "{info_path}"'])
    return swayutil.find_item({
        'app_id': 'capture',
        'name': self_title,
    })

# Build a tree of windows in the specified layout
def build_tree(tree, prompt, keep_prompt):
    if is_leaf(tree):
        build_leaf(tree, prompt, keep_prompt)
    else:
        build_tree(tree['subtrees'][0], prompt, keep_prompt)
        swayutil.swaymsg(['splitv'])
        for subtree in tree['subtrees'][1:]:
            build_tree(subtree, prompt, keep_prompt)
        swayutil.swaymsg([f'layout {tree["layout"]}'])
        swayutil.swaymsg(['focus parent'])

# Test for leaf, turn a leaf into a window, make a leaf targeting a window
def is_leaf(tree):
    return tree.get("subtrees") is None

def build_leaf(tree, prompt, keep_prompt):
    return make_random_window(tree, prompt, keep_prompt)

# Remove empty trees, flatten 1-trees
def clean_tree(tree):
    if is_leaf(tree):
        return tree

    subtree_count = len(tree['subtrees'])
    if subtree_count == 0:
        return None
    elif subtree_count == 1:
        return clean_tree(tree['subtrees'][0])
    else:
        return {
            'layout': tree['layout'],
            'subtrees': list(map(clean_tree, tree['subtrees']))
        }

# Set a workspace to contain a tree
def set_workspace(num, name, tree, prompt, keep_prompt):
    swayutil.swaymsg([f'workspace {num}'])
    swayutil.swaymsg([f'rename workspace {num} to "{name}"'])
    build_tree(clean_tree(tree), prompt, keep_prompt)

def build_workspaces(workspaces, prompt, keep_prompt):
    for workspace in workspaces:
        set_workspace(workspace['workspace_num'], workspace['workspace_name'], workspace, prompt, keep_prompt)

def main(args):
    build_workspaces(json.load(args.snapshot), args.prompt, args.keep_prompt)
