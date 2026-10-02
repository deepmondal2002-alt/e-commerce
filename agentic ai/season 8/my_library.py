import asyncio
import sys
import threading
from pathlib import Path

from langchain_mcp_adapters.tools import load_mcp_tools

connection = {
    "transport": "stdio",
    "command": sys.executable,
    "args": ["weather_server.py"],
    "cwd": str(Path(__file__).parent),
}


def _load_tools():
    return asyncio.run(load_mcp_tools(None, connection=connection))


def _load_in_thread():
    result = {}

    def runner():
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        original_stdin = sys.stdin
        import os
        try:
            with open(os.devnull, 'r+') as devnull:
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


tools = _load_in_thread()
