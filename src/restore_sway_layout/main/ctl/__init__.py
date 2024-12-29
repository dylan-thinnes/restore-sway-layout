import socket
from restore_sway_layout.util import socket_lines
import asyncio

async def dump_socket(sock):
    async for line in socket_lines(sock):
        print(line)

async def async_main(args):
    socket_file = args.socket_file
    with socket.socket(family=socket.AF_UNIX) as sock:
        sock.connect(socket_file)
        task = asyncio.create_task(dump_socket(sock))
        if args.query_id:
            sock.send(b'query-id\n')
        elif args.echo is not None:
            sock.send(b'echo\n' + args.echo.encode('utf-8') + b'\n')
        elif args.take_snapshot:
            sock.send(b'take-snapshot\n')
        elif args.take_snapshot_every is not None:
            sock.send(b'take-snapshot-every\n' + str(args.take_snapshot_every).encode('utf-8') + b'\n')
        sock.shutdown(socket.SHUT_WR)
        await task

def main(args):
    return asyncio.run(async_main(args))
