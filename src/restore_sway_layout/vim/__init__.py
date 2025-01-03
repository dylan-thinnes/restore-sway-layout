#!/usr/bin/env python3
from restore_sway_layout import swayutil
from restore_sway_layout import util
from glob import glob
import os
import psutil
import json
import sys
import re

# Read stored vim sessions
def read_vim_session(vim_id):
    vim_pid_path = os.path.join(os.environ['HOME'], ".vim-sessions", vim_id, "pid")
    vim_pid = util.read_file_to_int(vim_pid_path)
    vim_path_path = os.path.join(os.environ['HOME'], ".vim-sessions", vim_id, "path")
    vim_path = util.read_file_to_word(vim_path_path)
    return {
        'id': vim_id,
        'path': vim_path,
        'pid': vim_pid,
    }

@util.memoize
def read_all_vim_sessions():
    vim_ids = os.listdir(os.path.join(os.environ['HOME'], '.vim-sessions'))
    return [read_vim_session(vim_id) for vim_id in vim_ids]

# Find kitty node for a vim session's pid
def match_vim_pid_to_kitty(vim_pid, sway_tree):
    parent = psutil.Process(vim_pid)
    while parent.pid not in util.kitty_nodes(sway_tree) and parent is not None:
        parent = parent.parent()
    return parent.pid

# Save pertinent info for later recovery
def snapshot(node, sway_tree):
    kitty_to_vim = {}
    for vim_session in read_all_vim_sessions():
        if psutil.pid_exists(vim_session['pid']):
            kitty_pid = match_vim_pid_to_kitty(vim_session['pid'], sway_tree)
            vim_session['kitty_pid'] = kitty_pid
            kitty_to_vim[kitty_pid] = vim_session

    if node['app_id'] == 'kitty' and node['pid'] in kitty_to_vim:
        return kitty_to_vim[node['pid']]
    else:
        return None

def find_existing_instance(snapshot):
    if 'kitty_pid' in snapshot:
        node = swayutil.find_item({
            'app_id': 'kitty',
            'pid': snapshot['kitty_pid'],
        }, wait=False)
        if node is not None:
            return node
    return None

def restart(snapshot):
    vim_sessions = read_all_vim_sessions()
    matching_sessions = [session for session in vim_sessions if session['id'] == snapshot['id']]
    print(matching_sessions)

# Try to find using info from snapshot
def find(snapshot, self_title):
    existing_node = find_existing_instance(snapshot)
    if existing_node is not None:
        print(f'Found an existing instance searching for app_id = "kitty" and pid = {snapshot["kitty_pid"]}...')
        return node
    print("No existing instance found.")

    vim_pid = snapshot['pid']
    print(f"Looking for restored session, title = 'vim-restored-{vim_pid}'")
    return swayutil.find_item({
        'app_id': 'kitty',
        'name': f"vim-restored-{vim_pid}",
    })
