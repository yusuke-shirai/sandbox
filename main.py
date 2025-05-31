import asyncio
import os
from dotenv import load_dotenv
from langchain_core.messages.base import BaseMessage
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

    def send_message(self, message: str, stream_mode: str = "values"):
        if not self.agent:
            raise RuntimeError(
                "Agent not initialized. Use 'async with' context manager."
            )
        return self.agent.astream(
            {"messages": [{"role": "user", "content": message}]},
            debug=self.debug,
            stream_mode=stream_mode,
        )


if __name__ == "__main__":

    async def main():
        async with BrowserAgent(debug=False) as agent:
            # async for message_chunk, _ in agent.send_message(
            #     "Googleを開いてください", stream_mode="messages"
            # ):
            #     if message_chunk.content:
            #         print(message_chunk.content, end="|", flush=True)
            async for chunk in agent.send_message(
                "Googleを開いてください", stream_mode="updates"
            ):
                for _, v in chunk.items():
                    if "messages" in v:
                        for m in v["messages"]:
                            if isinstance(m, BaseMessage):
                                print(m.pretty_repr())
                            else:
                                print(m)
            input("Press Enter to continue...")

    asyncio.run(main())
