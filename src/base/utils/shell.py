import asyncio
from fastapi import WebSocket, WebSocketDisconnect


async def read_stream(stream, websocket: WebSocket):
    while True:
        line: str = await stream.readline()
        if not line:
            break
        decoded_line = line.decode().rstrip()
        await websocket.send_text(decoded_line)
    await websocket.send_text("/")


async def run_shell_cmd(cmd: str, websocket: WebSocket):
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Create tasks to read stdout and stderr concurrently
        stdout_task = asyncio.create_task(read_stream(proc.stdout, websocket))
        stderr_task = asyncio.create_task(read_stream(proc.stderr, websocket))

        # Wait for the subprocess to complete
        await proc.wait()

        # Ensure all output has been processed
        await stdout_task
        await stderr_task
    except asyncio.CancelledError:
        proc.terminate()
        await proc.wait()

    except WebSocketDisconnect:
        proc.terminate()
        await proc.wait()
