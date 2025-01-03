import socket
from restore_sway_layout.util import random_hex, print_stderr, socket_lines
from restore_sway_layout import snapshot
import tempfile
import os
import sys
import asyncio

from dbus_fast.service import ServiceInterface, method
from dbus_fast.aio import MessageBus

class DbusInterface(ServiceInterface):
    def __init__(self, socket_file):
        super().__init__('sway_restore_layout.interface')
        self.socket_file = socket_file

    @method()
    def GetSocketFile(self) -> 's':
        return self.socket_file

async def snapshot_every(starting_duration, new_duration_queue):
    duration = starting_duration
    while True:
        path = get_output_file()
        snapshot.save_snapshot(path)
        try:
            duration = await asyncio.wait_for(new_duration_queue.get(), duration)
        except asyncio.TimeoutError:
            pass

async def handle_commands(sock, tasks, new_duration_queue):
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
        elif command == 'update-snapshot':
            print_stderr(f"Taking snapshot...")
            snapshot.save_snapshot(get_output_file())
            print_stderr(f"Done!")
        elif command == 'set-rate':
            duration = float(await anext(line_generator))
            print_stderr(f'Taking a snapshot every {duration}')
            new_duration_queue.put_nowait(duration)
        else:
            print_stderr(f'Command `{command}` unrecognized')
        command = None
    sock.shutdown(socket.SHUT_WR)

def get_output_file():
    return os.path.join(output_dir, session_id + ".json")

async def setup_dbus(socket_file):
    bus = await MessageBus().connect()
    print_stderr(f'Found DBus...')
    interface = DbusInterface(socket_file)
    bus.export('/sway_restore_layout/instance', interface)
    await bus.request_name('sway_restore_layout.name')
    await asyncio.Event().wait()

def main(args):
    asyncio.run(async_main(args))

async def async_main(args):
    tasks = []

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
        task = asyncio.create_task(setup_dbus(socket_file))
        tasks.append(task)
        new_duration_queue = asyncio.Queue()
        task = asyncio.create_task(snapshot_every(args.rate, new_duration_queue))
        tasks.append(task)
        with socket.socket(family=socket.AF_UNIX) as sock:
            sock.bind(socket_file)
            sock.listen()
            if args.write_socket_to is not None:
                with open(args.write_socket_to, 'w+') as fd:
                    fd.write(socket_file)
                print_stderr(f'Wrote socket file name `{socket_file}` into file `{args.write_socket_to}`')
            else:
                print(socket_file)

            await handle_connections(sock, tasks, new_duration_queue)

    for task in tasks:
        await task

async def handle_connections(sock, tasks, new_duration_queue):
    while True:
        conn, conn_addr = await asyncio.to_thread(sock.accept)
        print_stderr(f'Started connection {conn}')
        task = asyncio.create_task(handle_commands(conn, tasks, new_duration_queue))
        tasks.append(task)
