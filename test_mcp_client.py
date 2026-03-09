import asyncio
import sys
from pathlib import Path
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

# Use the python binary from the virtual environment (don't resolve symlinks)
PYTHON_BIN = str(Path(".venv/bin/python3").absolute())
SERVER_SCRIPT = str(Path("microservices/storage/mcp_server.py").absolute())

async def test_connection():
    print(f"Connecting to {SERVER_SCRIPT} using {PYTHON_BIN}...")
    # Add PYTHONPATH env variable 
    env = {"PYTHONPATH": str(Path().absolute())}
    params = StdioServerParameters(command=PYTHON_BIN, args=[SERVER_SCRIPT], env=env)
    
    try:
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("✅ Connected successfully!")
                tools = await session.list_tools()
                print("Available Tools:")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
