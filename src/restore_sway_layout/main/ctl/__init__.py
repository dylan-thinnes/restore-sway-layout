import socket
from restore_sway_layout.util import print_stderr
import asyncio

from dbus_fast import Message, MessageType
from dbus_fast.aio import MessageBus

async def dump_socket(reader):
    async for raw_line in reader:
        line = raw_line.decode('utf-8').rstrip()
        print(line)

async def async_main(args):
    if args.dbus and args.socket_file is not None:
        print_stderr('Specified both --dbus and --socket-file, please only specify one.')
        return 1
    elif not args.dbus and args.socket_file is None:
        print_stderr('Neither --dbus nor --socket-file have been specified, please specify one.')
        return 1
    elif args.dbus:
        bus = await MessageBus().connect()
        reply = await bus.call(
            Message(destination='sway_restore_layout.name',
                    path='/sway_restore_layout/instance',
                    interface='sway_restore_layout.interface',
                    member='GetSocketFile',
                    message_type=MessageType.METHOD_CALL))
        if reply.message_type == MessageType.ERROR:
            print_stderr(f'Tried to query socket file from DBus, got an error instead:\n{reply.body[0]}')
            return 1
        socket_file = reply.body[0]
        print_stderr(f'Got socket file `{socket_file}` by querying DBus.')
    else:
        socket_file = args.socket_file
        print_stderr(f'Got socket file `{socket_file}` from args.')

    reader, writer = await asyncio.open_unix_connection(socket_file)
    task = asyncio.create_task(dump_socket(reader))
    if args.query_id:
        writer.write(b'query-id\n')
    elif args.echo is not None:
        writer.write(b'echo\n' + args.echo.encode('utf-8') + b'\n')
    elif args.update_snapshot:
        writer.write(b'update-snapshot\n')
    elif args.set_rate is not None:
        writer.write(b'set-rate\n' + str(args.set_rate).encode('utf-8') + b'\n')
    writer.write_eof()
    await writer.drain()
    await task

def main(args):
    return asyncio.run(async_main(args))
