#!/usr/bin/env python3
from restore_sway_layout import swayutil

# Always matches
def snapshot(node):
    if node.get('app_id') == 'firefox':
        return {
            'title': node['name'],
            'app_id': node['app_id'],
        }
    else:
        return None

# Find in the simplest way possible
def find(snapshot, self_title):
    print(f'Looking for a firefox window (app_id: "{snapshot["app_id"]}") with title:')
    print(snapshot["title"])
    return swayutil.find_item({
        'app_id': snapshot['app_id'],
        'name': snapshot['title'],
    })
