import argparse
import json

from restore_sway_layout.main import relocate
from restore_sway_layout.main import snapshot
from restore_sway_layout.main import restart

parser = argparse.ArgumentParser(prog='restore_sway_layout')
subparsers = parser.add_subparsers()

subparser_snapshot = subparsers.add_parser('snapshot', help='Snapshot the layout and state of workspaces')
subparser_snapshot.add_argument('--output', '-o', type=str, default='-')
subparser_snapshot.add_argument('--watch', '-w', type=int)
subparser_snapshot.add_argument('--append', action=argparse.BooleanOptionalAction, help='Append new snapshots to the output file instead of overwriting. This is always true if the output file is \'/dev/stdout\' or \'-\'')
subparser_snapshot.add_argument('workspace', nargs='*', type=float, help='Index of workspace to save. If unspecified, all workspaces are saved.')
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
