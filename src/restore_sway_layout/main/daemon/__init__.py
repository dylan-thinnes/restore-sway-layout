import socket
from restore_sway_layout.util import random_hex, print_stderr
from restore_sway_layout import snapshot
import tempfile
import os
import sys
import asyncio
from dataclasses import dataclass

from dbus_fast.service import ServiceInterface, method
from dbus_fast.aio import MessageBus

class DbusInterface(ServiceInterface):
    def __init__(self, socket_file):
        super().__init__('sway_restore_layout.interface')
        self.socket_file = socket_file

    @method()
    def GetSocketFile(self) -> 's': # type: ignore
        return self.socket_file

@dataclass
class DaemonConfig:
    output_dir: str
    session_id: str = random_hex(20)
    @property
    def output_file(self):
        return os.path.join(self.output_dir, self.session_id + ".json")

async def snapshot_every(starting_duration: float, new_duration_queue: asyncio.Queue[float], config: DaemonConfig):
    duration = starting_duration
    while True:
        path = config.output_file
        snapshot.save_snapshot_without_failure(path)
        try:
            duration = await asyncio.wait_for(new_duration_queue.get(), duration)
        except asyncio.TimeoutError:
            pass

async def handle_commands(reader, writer, new_duration_queue: asyncio.Queue[float], config: DaemonConfig):
    command = None
    async for raw_line in reader:
        line = raw_line.decode('utf-8').rstrip()
        if line == '':
            continue
        if command is None:
            command = line
        if command == 'query-id':
            print_stderr(f'Query ID: {config.session_id}')
            writer.write(config.session_id.encode('utf-8') + b'\n')
            await writer.drain()
        elif command == 'echo':
            print_stderr(f'Receiving line...')
            raw_line = await reader.readline()
            line = raw_line.decode('utf-8').rstrip()
            writer.write(line.encode('utf-8') + b'\n')
            await writer.drain()
            print_stderr(f'Received line: {line}')
        elif command == 'update-snapshot':
            print_stderr(f"Taking snapshot...")
            snapshot.save_snapshot_without_failure(config.output_file)
            print_stderr(f"Done!")
        elif command == 'set-rate':
            raw_line = await reader.readline()
            duration = float(raw_line.decode('utf-8').rstrip())
            print_stderr(f'Taking a snapshot every {duration}')
            new_duration_queue.put_nowait(duration)
        else:
            print_stderr(f'Command `{command}` unrecognized')
        command = None

    writer.write_eof()
    await writer.drain()

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
    if args.output is None:
        print_stderr("Must specify an output directory with --output")
        return
    elif not os.path.isdir(args.output):
        print_stderr(f"Output path `{args.output}` is not a directory")
        return

    config = DaemonConfig(args.output)

    with tempfile.TemporaryDirectory() as socket_dir:
        socket_file = os.path.join(socket_dir, f'restore-sway-layout-{config.session_id}-ipc.sock')
        dbus_task = asyncio.create_task(setup_dbus(socket_file))
        new_duration_queue: asyncio.Queue = asyncio.Queue()
        snapshot_task = asyncio.create_task(snapshot_every(args.rate, new_duration_queue, config))
        unix_socket_task = asyncio.create_task(asyncio.start_unix_server(
            lambda reader, writer: handle_commands(reader, writer, new_duration_queue, config), socket_file))

        if args.write_socket_to is not None:
            with open(args.write_socket_to, 'w+') as fd:
                fd.write(socket_file)
            print_stderr(f'Wrote socket file name `{socket_file}` into file `{args.write_socket_to}`')
        else:
            print(socket_file)

        await unix_socket_task
        await snapshot_task
        await dbus_task
