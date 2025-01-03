#!/usr/bin/env python3
import json
from restore_sway_layout import swayutil

# Always matches
def snapshot(node, sway_tree):
    if node.get('shell') == 'xwayland':
        return {
            'title': node['name'],
            'shell': 'xwayland',
            'window_properties': {
                'class': node['window_properties']['class'],
            },
        }
    else:
        return {
            'title': node['name'],
            'app_id': node['app_id'],
        }

# Find in the simplest way possible
def find(snapshot, self_title):
    if snapshot.get('shell') == 'xwayland':
        print(f'Looking for an xwayland node with properties:')
        print(json.dumps(snapshot))
        return swayutil.find_item({
            'window_properties': snapshot['window_properties'],
            'shell': snapshot['shell'],
            'name': snapshot['title'],
        })
    else:
        print(f'Looking for a ordinary node with properties:')
        print(json.dumps(snapshot))
        return swayutil.find_item({
            'app_id': snapshot['app_id'],
            'name': snapshot['title'],
        })
