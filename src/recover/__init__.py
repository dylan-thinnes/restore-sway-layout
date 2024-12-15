import argparse
import json

def snapshot(args):
    print('snapshot called!')
    print(args)

def restart(args):
    print('restart called!')
    print(args)

def relocate(args):
    print('relocate called!')
    print(args)

parser = argparse.ArgumentParser(prog='recover')
subparsers = parser.add_subparsers()

subparser_snapshot = subparsers.add_parser('snapshot', help='Snapshot the layout and state of workspaces')
subparser_snapshot.add_argument('--output', '-o', type=argparse.FileType('w'), default='-')
subparser_snapshot.add_argument('workspace', nargs='*', help='Index of workspace to save. If unspecified, all workspaces are saved.')
subparser_snapshot.set_defaults(func=snapshot)

subparser_restart = subparsers.add_parser('restart', help='Restart programs based on a snapshot')
subparser_restart.add_argument('snapshot', type=argparse.FileType('r'), default='-', help='File to read snapshot from, stdin by default')
subparser_restart.set_defaults(func=restart)

subparser_relocate = subparsers.add_parser('relocate', help='Relocate programs to locations based on a snapshot')
subparser_relocate.add_argument('snapshot', type=argparse.FileType('r'), default='-', help='File to read snapshot from, stdin by default')
subparser_relocate.add_argument('--prompt', action=argparse.BooleanOptionalAction, help='Prompt for confirmation before relocating a program')
subparser_relocate.set_defaults(func=relocate)

def main():
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
