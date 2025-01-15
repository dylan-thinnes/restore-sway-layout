from restore_sway_layout import swayutil
from restore_sway_layout import util
import subprocess

# Always matches
def snapshot(node):
    if node.get('app_id') == 'firefox':
        return {
            'title': node['name'],
            'app_id': node['app_id'],
        }
    else:
        return None

class Restarter():
    def __init__(self):
        self.seen = False

    def restart(self, type_, snapshot):
        if type_ == 'firefox':
            if not self.seen:
                self.seen = True
                util.print_stderr('Found an instance of firefox, restarting by running `firefox`...')
                return lambda: swayutil.swaymsg(['exec firefox -no-remote'])
            else:
                util.print_stderr('Found an instance of firefox, but we\'ve already run a restart command.')

# Find in the simplest way possible
def find(snapshot, self_title):
    print(f'Looking for a firefox window (app_id: "{snapshot["app_id"]}") with title:')
    print(snapshot["title"])
    return swayutil.find_item({
        'app_id': snapshot['app_id'],
        'name': snapshot['title'],
    })
