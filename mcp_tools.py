import asyncio
import os
import sys
import threading
from pathlib import Path

from langchain_mcp_adapters.tools import load_mcp_tools

PROJECT_ROOT = Path(__file__).resolve().parent

SERVER_PARAMS = {
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@cocal/google-calendar-mcp"],
    "cwd": str(PROJECT_ROOT),
    "env": {"GOOGLE_OAUTH_CREDENTIALS": str(PROJECT_ROOT / "gcp-oauth.keys.json")},
}


def get_client():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    server_params = StdioServerParameters(
        command=SERVER_PARAMS["command"],
        args=SERVER_PARAMS["args"],
        cwd=SERVER_PARAMS["cwd"],
        env=SERVER_PARAMS["env"],
    )

    async def _open():
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return session

    return asyncio.run(_open())


def _load_tools():
    return asyncio.run(load_mcp_tools(None, connection=SERVER_PARAMS))


def tools_session():
    result = {}

    def runner():
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        original_stdin = sys.stdin
        try:
            with open(os.devnull, "r+") as devnull:
                sys.stdout = devnull
                sys.stderr = devnull
                sys.stdin = devnull
                result["tools"] = _load_tools()
        except Exception as e:
            result["error"] = e
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            sys.stdin = original_stdin

    thread = threading.Thread(target=runner)
    thread.start()
    thread.join()

    if "error" in result:
        raise RuntimeError(f"Failed to load tools: {result['error']}") from result["error"]

    return result["tools"]
