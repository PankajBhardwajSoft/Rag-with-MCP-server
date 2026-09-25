import asyncio
from pathlib import Path

from fastmcp import Client


async def main() -> None:
    async with Client(Path("mcp_server.py")) as client:
        tools = await client.list_tools()
        print("TOOLS:", [tool.name for tool in tools])
        result = await client.call_tool(
            "ask_tesla_report",
            {"question": "What was Tesla revenue in 2023?"},
        )
        print("RESULT:", result)


if __name__ == "__main__":
    asyncio.run(main())
