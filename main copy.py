import asyncio
import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters, stdio_client


load_dotenv(override=True)

async def main():
    server_params = StdioServerParameters(
        command="npx", args=["@playwright/mcp@latest"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent("openai:gpt-4o-mini", tools)
            agent_response = await agent.ainvoke({"messages": "Yahoo! JAPANを開いてください"}, debug=True)
            print(agent_response)


if __name__ == "__main__":
    asyncio.run(main())
