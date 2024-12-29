#!/usr/bin/env python3
from restore_sway_layout import swayutil
from restore_sway_layout import util
from glob import glob
import os
import psutil
import json
import sys
import re

# Read stored zsh sessions
def read_zsh_session(zsh_id):
    zsh_pid_path = os.path.join(os.environ['HOME'], ".zsh-sessions", zsh_id, "pid")
    zsh_pid = util.read_file_to_int(zsh_pid_path)
    return {
        'id': zsh_id,
        'pid': zsh_pid,
    }

@util.memoize
def read_all_zsh_sessions():
    zsh_ids = os.listdir(os.path.join(os.environ['HOME'], '.zsh-sessions'))
    return [read_zsh_session(zsh_id) for zsh_id in zsh_ids]

# Find kitty node for a zsh session's pid
def match_zsh_pid_to_kitty(zsh_pid):
    parent = psutil.Process(zsh_pid)
    while parent.pid not in util.kitty_nodes() and parent is not None:
        parent = parent.parent()
    return parent.pid

# Save pertinent info for later recovery
def snapshot(node):
    kitty_to_zsh = {}
    for zsh_session in read_all_zsh_sessions():
        if psutil.pid_exists(zsh_session['pid']):
            kitty_pid = match_zsh_pid_to_kitty(zsh_session['pid'])
            zsh_session['kitty_pid'] = kitty_pid
            kitty_to_zsh[kitty_pid] = zsh_session

    if node['app_id'] == 'kitty' and node['pid'] in kitty_to_zsh:
        return kitty_to_zsh[node['pid']]
    else:
        return None

# Try to find using info from snapshot
def find(snapshot, self_title):
    if 'kitty_pid' in snapshot:
        print(f'Instance may still exist, searching for app_id = "kitty" and pid = {snapshot["kitty_pid"]}...')
        node = swayutil.find_item({
            'app_id': 'kitty',
            'pid': snapshot['kitty_pid'],
        }, wait=False)
        if node is not None:
            print("Found an instance.")
            return node
        print("Nothing found.")

    zsh_pid = snapshot['pid']
    print(f"Looking for restored session, title = 'zsh-restored-{zsh_pid}'")
    return swayutil.find_item({
        'app_id': 'kitty',
        'name': f"zsh-restored-{zsh_pid}",
    })
