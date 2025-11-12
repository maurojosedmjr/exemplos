import uuid
import json
import aiohttp
from typing import Optional

class MCPClient:
    def __init__(self, url: str):
        self.url = url
        self.session: Optional[aiohttp.ClientSession] = None
        self.mcp_session_id: Optional[str] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _get_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json,text/event-stream"
        }
        if self.mcp_session_id:
            headers["MCP-Session-ID"] = self.mcp_session_id
        return headers

    def _build_initialize_data(self) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

    def _build_call_tool_data(self, tool_name: str, **kwargs) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": self.mcp_session_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": kwargs or {}
            }
        }

    @staticmethod
    def _parse_response_data(text: str) -> dict:
        data = text.split("data: ")[-1]
        return json.loads(data)

    async def initialize(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

        async with self.session.post(
            self.url,
            headers=self._get_headers(),
            json=self._build_initialize_data()
        ) as response:
            self.mcp_session_id = response.headers.get("mcp-session-id")
            data = await response.text()
            
        print("Resposta de inicialização:", data)
        print("=" * 40)
        return data

    async def call_tool(self, tool_name: str, **kwargs) -> dict:
        if not self.session or not self.mcp_session_id:
            raise RuntimeError("Client not initialized. Call initialize() first.")

        async with self.session.post(
            self.url,
            headers=self._get_headers(),
            json=self._build_call_tool_data(tool_name, **kwargs)
        ) as response:
            data = await response.text()

        return self._parse_response_data(data)

async def main():
    async with MCPClient("http://127.0.0.1:8000/mcp") as client:
        await client.initialize()
        result = await client.call_tool("get_pokemon", **{"offset": 5, "limit": 5})
        print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
