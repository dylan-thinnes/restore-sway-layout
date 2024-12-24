#!/usr/bin/env python3
import sys
import subprocess
import ijson
import json
import time

from restore_sway_layout import swayutil
from restore_sway_layout import vim
from restore_sway_layout import zsh
from restore_sway_layout import generic
from restore_sway_layout import firefox

arg_path = sys.argv[1]
arg = json.load(open(arg_path))
self_title = arg['self_title']
type_ = arg['type']
snapshot = arg['snapshot']

arg_prompt = sys.argv[2]
prompt = int(arg_prompt) != 0

arg_keep_prompt = sys.argv[3]
keep_prompt = int(arg_keep_prompt) != 0

print(f"Self title: {self_title}")
print(f"Type: {type_}")
print(f"Snapshot: {snapshot}")

def find_node():
    match type_:
        case "zsh":
            return zsh.find(snapshot, self_title)
        case "firefox":
            return firefox.find(snapshot, self_title)
        case "vim":
            return vim.find(snapshot, self_title)
        case "generic":
            return generic.find(snapshot, self_title)
        case _:
            print(f'Unknown type {type_}')
            return None

def prompt_for_yes_or_no():
    print("Swap with this node? (y/n)")
    inp = sys.stdin.readline().strip().lower()
    if inp == 'y' or inp == 'yes':
        return True
    elif inp == 'n' or inp == 'no':
        return False
    else:
        print(f'Input \'{inp}\' is not "y", "yes", "n", or "no"')
        prompt_for_yes_or_no()

def swap_with_con_id(target_id):
    swayutil.swaymsg([f'[title="^{self_title}$"] swap container with con_id {target_id}'])

def main():
    while True:
        node = find_node()
        if node is None:
            return
            sys.stdin.readline()
        else:
            print("Found a matching node!")
            print(node)
            target_id = node['id']

            if prompt:
                use_node = prompt_for_yes_or_no()
                if use_node:
                    swap_with_con_id(target_id)
                    if keep_prompt:
                        while True:
                            print('Press enter to swap with this node again.')
                            sys.stdin.readline()
                            swap_with_con_id(target_id)
                    return
                else:
                    continue
            else:
                swap_with_con_id(target_id)
                return

main()
