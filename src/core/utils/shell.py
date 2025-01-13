"""Module to handle bash commands through subprocess"""

import asyncio
import os
from asyncio.subprocess import Process
from typing import AsyncGenerator
from uuid import UUID

processes = {}


async def create_process(client_id: UUID) -> Process:
    """Create a reusable subprocess."""
    if client_id in processes:
        return processes[client_id]

    # Dynamically get the home directory
    home_dir = os.path.expanduser("~")

    proc = await asyncio.create_subprocess_shell(
        "/bin/bash",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=home_dir,
    )
    processes[client_id] = proc
    return proc


def delete_process(client_id: UUID) -> Process:
    del processes[client_id]


async def stream_output(
    stream: asyncio.StreamReader,
    end_marker: str,
) -> AsyncGenerator[str]:
    """Stream output from a given stream and yield it"""
    while True:
        line: bytes = await stream.readline()
        if not line:  # End of the stream
            break
        line_decoded = line.decode().rstrip()
        if end_marker in line_decoded:  # End marker found
            break
        yield line_decoded
    yield "/"


async def run_command(
    *,
    process: Process,
    command: str,
) -> AsyncGenerator[str]:
    """Send a command to the process and read its output."""

    if not command.strip():
        yield "/"
        return

    end_marker = "EOF"
    process.stdin.write((f"{command}; echo {end_marker}\n").encode())
    await process.stdin.drain()

    async for stdout_line in stream_output(process.stdout, end_marker):
        yield stdout_line
