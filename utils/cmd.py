import subprocess
import asyncio
from utils import logger
from collections import deque
from utils.handlers import AsyncQueryRequestor
# import logger

logger = logger.setup_logger("cmd")

async def fork_command(command, issue_id="10001", comment_id="10002", requestor=None, sleep_time=10):
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    max_size = 20

    stdout, stderr = await proc.communicate()
    logger.info(f"Run: {command} -> Stdout: {stdout.decode()} -> Stderr: {stderr.decode()}")
    return stdout.decode(), stderr.decode()

async def main():
    res, err = await fork_command("uname -a")
    print(f"{res} === {err}")

if __name__ == "__main__":
    asyncio.run(main())
