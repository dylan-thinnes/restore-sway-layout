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

# Read stored zsh sessions
def read_zsh_session(zsh_id):
    zsh_pid_path = os.path.join(os.environ['HOME'], ".zsh-sessions", zsh_id, "pid")
    zsh_pid = util.read_file_to_int(zsh_pid_path)
    zsh_pwd_path = os.path.join(os.environ['HOME'], ".zsh-sessions", zsh_id, "pwd")
    zsh_pwd = util.read_file_to_word(zsh_pwd_path)
    return {
        'id': zsh_id,
        'pid': zsh_pid,
        'pwd': zsh_pwd,
    }

def read_all_zsh_sessions():
    zsh_ids = os.listdir(os.path.join(os.environ['HOME'], '.zsh-sessions'))
    return [read_zsh_session(zsh_id) for zsh_id in zsh_ids]

class Snapshotter():
    def __init__(self, sway_tree):
        self.sway_tree = sway_tree
        self.all_zsh_sessions = read_all_zsh_sessions()

    # Find kitty node for a zsh session's pid
    def match_zsh_pid_to_kitty(self, zsh_pid):
        parent = psutil.Process(zsh_pid)
        while parent.pid not in util.kitty_nodes(self.sway_tree) and parent is not None:
            parent = parent.parent()
        return parent.pid

    # Save pertinent info for later recovery
    def snapshot(self, node):
        kitty_to_zsh = {}
        for zsh_session in self.all_zsh_sessions:
            if psutil.pid_exists(zsh_session['pid']):
                kitty_pid = self.match_zsh_pid_to_kitty(zsh_session['pid'])
                zsh_session['kitty_pid'] = kitty_pid
                kitty_to_zsh[kitty_pid] = zsh_session

        if node['app_id'] == 'kitty' and node['pid'] in kitty_to_zsh:
            return kitty_to_zsh[node['pid']]
        else:
            return None

class Restarter():
    def __init__(self, sway_tree):
        self.sway_tree = sway_tree
        self.all_zsh_sessions = read_all_zsh_sessions()

    def restart(self, type_, snapshot):
        if type_ == 'zsh':
            existing_node = find_existing_instance(snapshot, self.sway_tree)
            if existing_node is not None:
                print(f'Info: Not restarting zsh snapshot node {snapshot} because it is already running.')
                pass
            else:
                matching_sessions = [session for session in self.all_zsh_sessions if session['id'] == snapshot['id']]
                if len(matching_sessions) == 1:
                    return lambda: self.restart_one(matching_sessions[0])
                elif len(matching_sessions) > 1:
                    print(f'Warning: More than one zsh session matched snapshot {snapshot}, this should not happen!')
                    pass
                else:
                    pass
        return None

    def restart_one(self, session):
        print('Restart one: ', session)
        tmpdir = tempfile.mkdtemp()
        src_zsh_session = os.path.join(os.environ['HOME'], ".zsh-sessions", session['id'])
        src_zsh_session_env = os.path.join(src_zsh_session, "env")
        dst_zsh_session_env = os.path.join(tmpdir, 'env')
        shutil.copyfile(src_zsh_session_env, dst_zsh_session_env)
        shutil.rmtree(src_zsh_session)
        return subprocess.run(['kitty', '-d', session['pwd'], '--detach', '--title', f"zsh-restored-{session['pid']}", '--', 'zsh', '-is', 'source', dst_zsh_session_env])

def find_existing_instance(snapshot, existing_tree=None):
    if 'kitty_pid' in snapshot:
        node = swayutil.find_item({
            'app_id': 'kitty',
            'pid': snapshot['kitty_pid'],
        }, wait=False, existing_tree=existing_tree)
        if node is not None:
            return node
    return None

# Try to find using info from snapshot
def find(snapshot, self_title):
    existing_node = find_existing_instance(snapshot)
    if existing_node is not None:
        print(f'Found an existing instance searching for app_id = "kitty" and pid = {snapshot["kitty_pid"]}...')
        return existing_node
    print("No existing instance found.")

    zsh_pid = snapshot['pid']
    print(f"Looking for restored session, title = 'zsh-restored-{zsh_pid}'")
    return swayutil.find_item({
        'app_id': 'kitty',
        'name': f"zsh-restored-{zsh_pid}",
    })
