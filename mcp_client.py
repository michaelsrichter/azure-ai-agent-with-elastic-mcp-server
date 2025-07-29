"""
MCP (Model Context Protocol) Client for Elasticsearch integration.
Handles communication with the MCP server running on localhost:8080/mcp.
Uses Server-Sent Events (SSE) protocol.
"""

import json
import logging
import os
import uuid
from typing import Dict, List, Any, Optional
import httpx
from config import config

try:
    from azure.identity import DefaultAzureCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with the MCP server using SSE protocol."""
    
    def __init__(self, base_url: str = None):
        """Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP server. Defaults to config value.
        """
        self.base_url = base_url or config.mcp_server_url
        self.session_id = str(uuid.uuid4())
        self.client = httpx.AsyncClient(timeout=30.0)
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
        self._azure_credential = None
        
        # Initialize Azure authentication if the URL suggests it's needed
        if self._is_azure_devtunnel(self.base_url) and AZURE_AVAILABLE:
            logger.info("Detected devtunnel URL, initializing Azure authentication...")
            try:
                self._azure_credential = DefaultAzureCredential()
                logger.info("Azure authentication initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Azure authentication: {e}")
    
    def _is_azure_devtunnel(self, url: str) -> bool:
        """Check if URL is an Azure devtunnel that might require authentication."""
        return "devtunnels.ms" in url.lower()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def _get_headers(self):
        """Get headers for MCP requests, including devtunnel authentication if needed."""
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "X-Session-ID": self.session_id,
            "Cache-Control": "no-cache"
        }
        
        # Handle devtunnel authentication
        if self._is_azure_devtunnel(self.base_url):
            # Check for tunnel access token in environment
            tunnel_token = os.getenv("DEVTUNNEL_ACCESS_TOKEN")
            if tunnel_token:
                headers["X-Tunnel-Authorization"] = f"tunnel {tunnel_token}"
                logger.info("Added devtunnel access token from environment")
            elif self._azure_credential:
                try:
                    # Try to get Azure token for tunnel service
                    # This might work if the user is authenticated and has access
                    token = self._azure_credential.get_token("499b84ac-1321-427f-aa17-267ca6975798/.default")  # Visual Studio tunnel service
                    headers["X-Tunnel-Authorization"] = f"tunnel {token.token}"
                    logger.info("Added Azure-based tunnel authentication token")
                except Exception as e:
                    logger.warning(f"Failed to get tunnel authentication token: {e}")
                    logger.info("Consider setting DEVTUNNEL_ACCESS_TOKEN environment variable or configuring anonymous access")
        
        return headers
    
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
            headers = await self._get_headers()  # Now async call
            response = await self.client.post(
                self.base_url,
                headers=headers,
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
            
            logger.info(f"Tool {tool_name} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            raise
    
    # Convenience methods for Elasticsearch tools
    async def search_elasticsearch(self, query: str, index: str = None, size: int = 10) -> Dict[str, Any]:
        """Search Elasticsearch using the MCP server's search tool."""
        search_args = {
            "index": index or config.elasticsearch_index or "_all",
            "query_body": {
                "query": {
                    "query_string": {
                        "query": query
                    }
                },
                "size": size
            }
        }
        
        return await self.call_tool("search", search_args)
    
    async def get_elasticsearch_mapping(self, index: str = None) -> Dict[str, Any]:
        """Get the mapping for an Elasticsearch index."""
        mapping_args = {
            "index": index or config.elasticsearch_index or "_all"
        }
        
        return await self.call_tool("get_mappings", mapping_args)
    
    async def list_elasticsearch_indices(self, pattern: str = "*") -> Dict[str, Any]:
        """List Elasticsearch indices."""
        return await self.call_tool("list_indices", {"index_pattern": pattern})
    
    async def get_elasticsearch_shards(self) -> Dict[str, Any]:
        """Get Elasticsearch shard information."""
        return await self.call_tool("get_shards", {})
    
    async def esql_query(self, query: str) -> Dict[str, Any]:
        """Execute an ES|QL query."""
        return await self.call_tool("esql", {"query": query})


async def create_mcp_client() -> MCPClient:
    """Create and return an MCP client instance."""
    return MCPClient()
