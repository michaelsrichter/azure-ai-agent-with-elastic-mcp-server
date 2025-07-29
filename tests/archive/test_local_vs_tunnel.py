#!/usr/bin/env python3
"""
Test to verify MCP functionality works locally vs devtunnel authentication issue
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

async def test_local_vs_devtunnel():
    """Compare local MCP server vs devtunnel access."""
    
    # Test 1: Local MCP server
    logger.info("=== Testing Local MCP Server ===")
    try:
        local_client = MCPClient("http://localhost:8080/mcp")
        tools = await local_client.get_available_tools()
        logger.info(f"✅ Local connection successful! Found {len(tools)} tools")
        
        # Test search locally
        search_params = {
            "query_body": {
                "query": {"match_all": {}},
                "size": 1
            }
        }
        result = await local_client.call_tool("search", search_params)
        logger.info("✅ Local search test successful!")
        await local_client.close()
        
    except Exception as e:
        logger.error(f"❌ Local connection failed: {e}")
    
    # Test 2: DevTunnel
    logger.info("\n=== Testing DevTunnel ===")
    devtunnel_url = os.getenv("MCP_SERVER_URL")
    if devtunnel_url and "devtunnels.ms" in devtunnel_url:
        try:
            tunnel_client = MCPClient(devtunnel_url)
            tools = await tunnel_client.get_available_tools()
            logger.info(f"✅ DevTunnel connection successful! Found {len(tools)} tools")
            await tunnel_client.close()
            
        except Exception as e:
            logger.error(f"❌ DevTunnel connection failed: {e}")
            logger.info("This confirms the issue is with devtunnel authentication")
    else:
        logger.info("No devtunnel URL configured in MCP_SERVER_URL")
    
    logger.info("\n=== Summary ===")
    logger.info("If local works but devtunnel fails, the issue is devtunnel authentication.")
    logger.info("See DEVTUNNEL_AUTH_GUIDE.md for solutions.")

if __name__ == "__main__":
    asyncio.run(test_local_vs_devtunnel())
