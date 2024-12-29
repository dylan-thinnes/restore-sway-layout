import socket
from restore_sway_layout.util import random_hex, print_stderr, socket_lines
from restore_sway_layout import snapshot
import tempfile
import os
import sys
import asyncio

async def snapshot_every(duration):
    while True:
        snapshot.save_snapshot(get_output_file())
        asyncio.sleep(duration)

async def handle_commands(sock):
    line_generator = socket_lines(sock)
    command = None
    async for line in line_generator:
        if command is None:
            command = line
        if command == 'query-id':
            print_stderr(f'Query ID: {session_id}')
            sock.send(session_id.encode('utf-8') + b'\n')
        elif command == 'echo':
            print_stderr(f'Receiving line:')
            received_line = await anext(line_generator)
            sock.send(received_line.encode('utf-8') + b'\n')
            print_stderr(received_line)
        elif command == 'take-snapshot':
            print_stderr(f"Taking snapshot...")
            snapshot.save_snapshot(get_output_file())
            print_stderr(f"Done!")
        elif command == 'take-snapshot-every':
            duration = float(await anext(line_generator))
            print_stderr(f'Taking a snapshot every {duration}')
            asyncio.create_task(snapshot_every(duration))
        else:
            print_stderr(f'Command `{command}` unrecognized')
        command = None
    sock.shutdown(socket.SHUT_WR)

def get_output_file():
    return os.path.join(output_dir, session_id + ".json")

def main(args):
    if args.output is None:
        print_stderr("Must specify an output directory with --output")
        return
    elif not os.path.isdir(args.output):
        print_stderr(f"Output path `{args.output}` is not a directory")
        return

    global session_id, output_dir
    session_id = random_hex(20)
    output_dir = args.output

    with tempfile.TemporaryDirectory() as socket_dir:
        socket_file = os.path.join(socket_dir, f'restore-sway-layout-{session_id}-ipc.sock')
        with socket.socket(family=socket.AF_UNIX) as sock:
            print(socket_file)
            sock.bind(socket_file)
            sock.listen()
            asyncio.run(handle_connections(sock))

async def handle_connections(sock):
    while True:
        conn, conn_addr = await asyncio.to_thread(sock.accept)
        print_stderr(f'Started connection {conn}')
        asyncio.create_task(handle_commands(conn))
