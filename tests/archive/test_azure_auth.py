#!/usr/bin/env python3
"""
Test Azure authentication with devtunnel MCP server
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from mcp_client import MCPClient

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_azure_auth():
    """Test Azure authentication with devtunnel MCP server."""
    mcp_server_url = os.getenv("MCP_SERVER_URL")
    if not mcp_server_url:
        logger.error("MCP_SERVER_URL not found in environment")
        return
    
    logger.info(f"Testing Azure authentication with: {mcp_server_url}")
    
    try:
        # Create MCP client
        mcp_client = MCPClient(mcp_server_url)
        
        # Test connection with Azure authentication
        logger.info("Testing connection with Azure authentication...")
        tools = await mcp_client.get_available_tools()
        
        logger.info(f"Successfully connected! Found {len(tools)} tools:")
        for tool in tools:
            logger.info(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        
        # Test search tool specifically
        logger.info("\nTesting search tool...")
        search_params = {
            "query_body": {
                "query": {
                    "match_all": {}
                },
                "size": 3
            }
        }
        
        result = await mcp_client.call_tool("search", search_params)
        logger.info("Search tool test successful!")
        
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"]
            if isinstance(content, list) and content:
                logger.info(f"Found {len(content)} search results")
                for i, item in enumerate(content[:3]):  # Show first 3
                    if isinstance(item, dict) and "text" in item:
                        logger.info(f"  Result {i+1}: {item['text'][:100]}...")
        
        await mcp_client.close()
        logger.info("✅ Azure authentication test successful!")
        
    except Exception as e:
        logger.error(f"❌ Authentication test failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response text: {e.response.text}")

if __name__ == "__main__":
    asyncio.run(test_azure_auth())
