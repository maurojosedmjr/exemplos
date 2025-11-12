#estudo mcp
from typing import Optional
import aiohttp
import asyncio
import json
import traceback
import uuid

from mcp import ClientSession
from mcp.types import CallToolResult
from mcp.client.streamable_http import streamablehttp_client

# O URL do seu servidor MCP (ou do LiteLLM Proxy Gateway)
MCP_SERVER_URL = "http://127.0.0.1:8000/mcp" 

async def get_mcp_session():
    print(f"Tentando conectar e iniciar sessão MCP em: {MCP_SERVER_URL}")
    
    try:
        async with streamablehttp_client(url=MCP_SERVER_URL) as streams:
            read_stream, write_stream = streams[0], streams[1]
            async with ClientSession(read_stream, write_stream) as session:
                
                await session.initialize()
                
                print("✅ Sessão MCP inicializada com sucesso!")
                
                tools = await session.list_tools()
                print(f"Ferramentas disponíveis: {tools.tools}")
                
                
    except Exception as e:
        traceback.print_exc()
        print(f"❌ Erro na conexão ou sessão MCP: {e}")
        print("Verifique se o servidor está rodando no URL especificado.")


async def call_mcp_tool(tool_name: str, **kwargs) -> CallToolResult:
    print(f"Tentando conectar e iniciar sessão MCP em: {MCP_SERVER_URL}")
    
    try:
        async with streamablehttp_client(url=MCP_SERVER_URL) as streams:
            read_stream, write_stream = streams[0], streams[1]
            
            async with ClientSession(read_stream, write_stream) as session:
                
                await session.initialize()
                
                ans = await session.call_tool(tool_name, arguments=kwargs or {})
                return ans
    except Exception as err:
        print(err)


def _data_initialize() -> dict:
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

def _headers(mcp_session_id: Optional[str] = None) -> dict:
    ans: dict = {
        "Content-Type": "application/json",
        "Accept": "application/json,text/event-stream"
    }
    mcp_session_id and ans.update({"MCP-Session-ID": mcp_session_id})
    return ans


def _data_call_tool(tool_name: str, mcp_session_id: str, **kwargs):
    return {
        "jsonrpc": "2.0",
        "id": mcp_session_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": kwargs or {}
        }
    }


def get_data_from_response(text: str) -> dict:
    data = text.split("data: ")[-1]
    return json.loads(data)


async def outro_metodo(url: str, tool_name: str, **kwargs) -> dict:
    async with aiohttp.ClientSession() as http_session:
        async with http_session.post(url, headers=_headers(), json=_data_initialize()) as response:
            data_headers = response.headers
            data = await response.text()
        print("Resposta de inicialização:", data)
        print("=========" * 19)
        mcp_session_id: str = data_headers.get("mcp-session-id")
        async with http_session.post(url, headers=_headers(mcp_session_id), json=_data_call_tool(tool_name, mcp_session_id, **kwargs)) as response:
            data = await response.text()
    return get_data_from_response(data)


if __name__ == "__main__":
    asyncio.run(get_mcp_session())
    print("=========" * 19)
    ans = asyncio.run(outro_metodo("http://127.0.0.1:8000/mcp", "get_pokemon", **{"offset": 5, "limit": 5}))
    print(ans)
