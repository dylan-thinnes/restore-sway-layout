import tkinter as tk
from tkinter import N, S, E, W
import io

import sys
import random
from restore_sway_layout import swayutil
import asyncio

class TkLog(io.IOBase):
    def __init__(self):
        self.title = "tk-log-{:020d}".format(random.randint(0, 9999999999999999999))

        root = tk.Tk()
        root.title(self.title)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.root = root

        frame = tk.Frame(root)
        frame.grid(column=0, row=0, sticky=(N, S, E, W))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Create text box
        text = tk.Text(frame, foreground='white', background='black')
        text['relief'] = tk.FLAT
        text['highlightthickness'] = 0
        text.grid(column=0, row=0, sticky=(N, S, E, W))
        self.text = text

        # Set up scrollbar
        text_yscroll = tk.Scrollbar(frame, orient='vertical', command=text.yview)
        text_yscroll.grid(column=1, row=0, sticky='ns')
        text['yscrollcommand'] = text_yscroll.set

        self.root.update()
        swayutil.find_item({'name': self.title})

    async def run_loop(self):
        while True:
            await asyncio.sleep(1 / 30)
            self.root.update()

    # Override default implementation to say this log is writeable
    def writeable(self):
        return True

    # `read` is not provided by IOBase, have to stub it out ourselves
    def read(self, *args, **kwargs):
        raise io.UnsupportedOperation('read')

    def write(self, msg):
        self.text['state'] = 'normal'
        self.text.insert('end', msg)
        self.text.yview('end')
        self.text['state'] = 'disabled'

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.root.destroy()

    def make(task_creator):
        log = TkLog()
        task = task_creator.create_task(log.run_loop())
        return log, task

async def async_main():
    log1, task1 = TkLog.make(asyncio)
    log2, task2 = TkLog.make(asyncio)

    with log1, log2:
        i = 0
        user_input = asyncio.create_task(asyncio.to_thread(sys.stdin.readline))
        while True:
            i += 1
            timeout = asyncio.create_task(asyncio.sleep(1))
            done, pending = await asyncio.wait([user_input, timeout], return_when=asyncio.FIRST_COMPLETED)
            if user_input in done:
                print(f'Log 1, #{i}', file=log1)
                print(f'Log 2, #{i}', file=log2)
                user_input = asyncio.create_task(asyncio.to_thread(sys.stdin.readline))

    await task1
    await task2

def main():
    asyncio.run(async_main())
