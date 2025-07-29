#!/usr/bin/env python3
"""
Working MCP Client that properly handles Server-Sent Events (SSE) responses.
"""

import asyncio
import httpx
import json
import uuid
import logging
from typing import Dict, List, Any, Optional
from config import config

logger = logging.getLogger(__name__)


class WorkingMCPClient:
    """MCP Client that properly parses SSE responses."""
    
    def __init__(self, base_url: str = None):
        """Initialize the working MCP client."""
        self.base_url = base_url or config.mcp_server_url
        self.session_id = str(uuid.uuid4())
        self.client = httpx.AsyncClient(timeout=30.0)
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _get_headers(self):
        """Get headers for MCP requests."""
        return {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "X-Session-ID": self.session_id,
            "Cache-Control": "no-cache"
        }
    
    def _parse_sse_response(self, sse_text: str) -> Dict[str, Any]:
        """Parse Server-Sent Events response."""
        lines = sse_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('data: '):
                # Extract JSON after 'data: '
                json_data = line[6:]  # Remove 'data: ' prefix
                try:
                    return json.loads(json_data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse SSE JSON: {e}")
                    logger.error(f"Raw JSON data: {json_data[:200]}...")
                    raise Exception(f"Invalid JSON in SSE response: {e}")
        
        raise Exception("No data found in SSE response")
    
    async def _send_mcp_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a request to the MCP server and parse SSE response."""
        request_id = str(uuid.uuid4())
        
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }
        
        logger.debug(f"Sending MCP request: {method}")
        
        try:
            response = await self.client.post(
                self.base_url,
                headers=self._get_headers(),
                json=payload
            )
            
            response.raise_for_status()
            
            # Parse SSE response
            sse_text = response.text
            parsed_response = self._parse_sse_response(sse_text)
            
            # Check for JSON-RPC error
            if "error" in parsed_response:
                error = parsed_response["error"]
                raise Exception(f"MCP server error: {error}")
            
            # Return the result
            return parsed_response.get("result", parsed_response)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise Exception(f"MCP server HTTP error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error in MCP request: {e}")
            raise
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from MCP server."""
        if self._tools_cache is not None:
            return self._tools_cache
        
        try:
            result = await self._send_mcp_request("tools/list")
            
            # Extract tools from result
            if "tools" in result:
                self._tools_cache = result["tools"]
            elif isinstance(result, list):
                self._tools_cache = result
            else:
                self._tools_cache = []
            
            logger.info(f"Retrieved {len(self._tools_cache)} tools from MCP server")
            return self._tools_cache
            
        except Exception as e:
            logger.error(f"Failed to get tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        try:
            result = await self._send_mcp_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            raise
    
    # Convenience methods for Elasticsearch
    async def search_elasticsearch(self, query: str, index: str = None, size: int = 10) -> Dict[str, Any]:
        """Search Elasticsearch via MCP."""
        params = {
            "query": query,
            "size": size
        }
        if index:
            params["index"] = index
        
        return await self.call_tool("elasticsearch_search", params)
    
    async def get_elasticsearch_mapping(self, index: str = None) -> Dict[str, Any]:
        """Get Elasticsearch mapping via MCP."""
        params = {}
        if index:
            params["index"] = index
        
        return await self.call_tool("get_mappings", params)


def create_working_mcp_client() -> WorkingMCPClient:
    """Create and return a working MCP client."""
    return WorkingMCPClient()


async def test_working_mcp_client():
    """Test the working MCP client."""
    print("🎯 Testing Working MCP Client")
    print("=" * 50)
    
    try:
        async with create_working_mcp_client() as client:
            print(f"✓ Client created with session ID: {client.session_id}")
            
            # Test getting tools
            tools = await client.get_available_tools()
            print(f"✓ Found {len(tools)} tools:")
            
            for tool in tools:
                name = tool.get('name', 'Unknown')
                description = tool.get('description', 'No description')[:80]
                schema = tool.get('inputSchema', {})
                required = schema.get('required', [])
                print(f"  - {name}: {description}")
                print(f"    Required params: {required}")
            
            # Test calling a tool if available
            if tools:
                # Look for a tool that doesn't require parameters
                simple_tools = [t for t in tools if not t.get('inputSchema', {}).get('required', [])]
                
                if simple_tools:
                    tool = simple_tools[0]
                    tool_name = tool.get('name')
                    print(f"\n🧪 Testing tool call: {tool_name}")
                    
                    try:
                        result = await client.call_tool(tool_name, {})
                        print(f"✓ Tool call successful")
                        print(f"Result: {str(result)[:300]}...")
                    except Exception as e:
                        print(f"⚠️  Tool call failed: {e}")
                else:
                    # Try a tool with required parameters
                    tool = tools[0]
                    tool_name = tool.get('name')
                    print(f"\n🧪 Testing tool call: {tool_name} (with parameters)")
                    
                    # Try to provide reasonable default parameters
                    if tool_name == "get_mappings":
                        try:
                            result = await client.call_tool(tool_name, {"index": "_all"})
                            print(f"✓ Tool call successful")
                            print(f"Result: {str(result)[:300]}...")
                        except Exception as e:
                            print(f"⚠️  Tool call failed: {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ Working MCP client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_working_mcp_client())
