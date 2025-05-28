import asyncio
import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters, stdio_client


load_dotenv(override=True)

class BrowserAgent:
    def __init__(self, debug=False):
        self.debug = debug
        self.client = None
        self.session = None
        self.agent = None

    async def __aenter__(self):
        server_params = StdioServerParameters(
            command="npx", args=["@playwright/mcp@latest"]
        )
        self.client = stdio_client(server_params)
        r, w = await self.client.__aenter__()
        self.session = await ClientSession(r, w).__aenter__()
        await self.session.initialize()
        tools = await load_mcp_tools(self.session)
        self.agent = create_react_agent("openai:gpt-4o-mini", tools)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def send_message(self, message: str):
        if not self.agent:
            raise RuntimeError("Agent not initialized. Use 'async with' context manager.")
        agent_response = await self.agent.ainvoke({"messages": message}, debug=self.debug)
        return agent_response


if __name__ == "__main__":
    async def main():
        async with BrowserAgent(debug=False) as agent:
            await agent.send_message("Yahoo! JAPANを開いてください")
            await agent.send_message("検索ボックスに「天気」と入力してください")
            input("Press Enter to continue...")

    asyncio.run(main())
