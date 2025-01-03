import argparse
import json

from restore_sway_layout.main import relocate
from restore_sway_layout.main import snapshot
from restore_sway_layout.main import restart
from restore_sway_layout.main import daemon
from restore_sway_layout.main import ctl

parser = argparse.ArgumentParser(prog='restore_sway_layout')
subparsers = parser.add_subparsers()

subparser_daemon = subparsers.add_parser('daemon', help='Start a daemon. Outputs IPC socket name.')
#subparser_daemon.add_argument('--socket-name', '-s', type=str, help='Path on which to create the daemon\'s IPC socket. A random socket is chosen if unspecified.')
#subparser_daemon.add_argument('--session-id', '-i', type=str, help='Session ID to use. If unspecified, a random 20-digit hex will be used.')
subparser_daemon.add_argument('--write-socket-to', type=str, help='Filepath to which to write the name of the socket. If unspecified, the socket name will be printed to stdout.', default=None)
subparser_daemon.add_argument('--rate', '-r', type=int, required=True)
subparser_daemon.add_argument('--output', type=str, default=None)
subparser_daemon.set_defaults(func=daemon.main)

subparser_ctl = subparsers.add_parser('ctl', help='Control a running daemon remotely')
subparser_ctl.add_argument('--socket-file', '-s', type=str, help='Path of socket file')
subparser_ctl.add_argument('--dbus', '-d', action=argparse.BooleanOptionalAction, help='Use DBus to discover socket file')
subparser_ctl.add_argument('--query-id', action=argparse.BooleanOptionalAction)
subparser_ctl.add_argument('--echo', type=str, help=argparse.SUPPRESS)
subparser_ctl.add_argument('--update-snapshot', action=argparse.BooleanOptionalAction)
subparser_ctl.add_argument('--set-rate', type=int, default=None)
subparser_ctl.set_defaults(func=ctl.main)

subparser_snapshot = subparsers.add_parser('snapshot', help='Snapshot the layout and state of workspaces')
subparser_snapshot.add_argument('--output', '-o', type=str, default='-')
subparser_snapshot.set_defaults(func=snapshot.main)

subparser_restart = subparsers.add_parser('restart', help='Restart programs based on a snapshot (not yet implemented)')
subparser_restart.add_argument('snapshot', type=argparse.FileType('r'), default='-', nargs='?', help='File to read snapshot from, stdin by default')
subparser_restart.set_defaults(func=restart.main)

subparser_relocate = subparsers.add_parser('relocate', help='Relocate programs to locations based on a snapshot')
subparser_relocate.add_argument('snapshot', type=argparse.FileType('r'), default='-', nargs='?', help='File to read snapshot from, stdin by default')
subparser_relocate.add_argument('--prompt', action=argparse.BooleanOptionalAction, help='Prompt for confirmation before relocating a program')
subparser_relocate.add_argument('--keep-prompt', action=argparse.BooleanOptionalAction, help='After relocating a program, keep the relocation window open for swapping back')
subparser_relocate.set_defaults(func=relocate.main)

def main():
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
