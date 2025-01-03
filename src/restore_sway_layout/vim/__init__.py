#!/usr/bin/env python3
from restore_sway_layout import swayutil
from restore_sway_layout import util
from glob import glob
import os
import psutil
import json
import sys
import re
import tempfile
import shutil
import subprocess

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

def read_all_vim_sessions():
    vim_ids = os.listdir(os.path.join(os.environ['HOME'], '.vim-sessions'))
    return [read_vim_session(vim_id) for vim_id in vim_ids]

class Snapshotter():
    def __init__(self, sway_tree):
        self.sway_tree = sway_tree
        self.all_vim_sessions = read_all_vim_sessions()

    # Save pertinent info for later recovery
    def snapshot(self, node):
        kitty_to_vim = {}
        for vim_session in self.all_vim_sessions:
            if psutil.pid_exists(vim_session['pid']):
                kitty_pid = self.match_vim_pid_to_kitty(vim_session['pid'])
                vim_session['kitty_pid'] = kitty_pid
                kitty_to_vim[kitty_pid] = vim_session

        if node['app_id'] == 'kitty' and node['pid'] in kitty_to_vim:
            return kitty_to_vim[node['pid']]
        else:
            return None

    # Find kitty node for a vim session's pid
    def match_vim_pid_to_kitty(self, vim_pid):
        parent = psutil.Process(vim_pid)
        while parent.pid not in util.kitty_nodes(self.sway_tree) and parent is not None:
            parent = parent.parent()
        return parent.pid

def find_existing_instance(snapshot, existing_tree=None):
    if 'kitty_pid' in snapshot:
        node = swayutil.find_item({
            'app_id': 'kitty',
            'pid': snapshot['kitty_pid'],
        }, wait=False, existing_tree=existing_tree)
        if node is not None:
            return node
    return None

class Restarter():
    def __init__(self, sway_tree):
        self.sway_tree = sway_tree
        self.all_vim_sessions = read_all_vim_sessions()

    def restart(self, type_, snapshot):
        if type_ == 'vim':
            existing_node = find_existing_instance(snapshot, self.sway_tree)
            if existing_node is not None:
                print(f'Info: Not restarting vim snapshot node {snapshot} because it is already running.')
                pass
            else:
                matching_sessions = [session for session in self.all_vim_sessions if session['id'] == snapshot['id']]
                if len(matching_sessions) == 1:
                    return lambda: self.restart_one(matching_sessions[0])
                elif len(matching_sessions) > 1:
                    print(f'Warning: More than one vim session matched snapshot {snapshot}, this should not happen!')
                    pass
                else:
                    pass
        return None

    def restart_one(self, session):
        print('Restart one: ', session)
        tmpdir = tempfile.mkdtemp()
        src_vim_session = os.path.join(os.environ['HOME'], ".vim-sessions", session['id'])
        src_vim_session_file = os.path.join(src_vim_session, "session.vim")
        dst_vim_session_file = os.path.join(tmpdir, 'session.vim')
        shutil.copyfile(src_vim_session_file, dst_vim_session_file)
        shutil.rmtree(src_vim_session)
        return subprocess.run(['kitty', '-d', session['path'], '--detach', '--title', f"vim-restored-{session['pid']}", '--', 'zsh', '-is', 'eval', 'vim', '-S', dst_vim_session_file])

# Try to find using info from snapshot
def find(snapshot, self_title):
    existing_node = find_existing_instance(snapshot)
    if existing_node is not None:
        print(f'Found an existing instance searching for app_id = "kitty" and pid = {snapshot["kitty_pid"]}...')
        return existing_node
    print("No existing instance found.")

    vim_pid = snapshot['pid']
    print(f"Looking for restored session, title = 'vim-restored-{vim_pid}'")
    return swayutil.find_item({
        'app_id': 'kitty',
        'name': f"vim-restored-{vim_pid}",
    })
