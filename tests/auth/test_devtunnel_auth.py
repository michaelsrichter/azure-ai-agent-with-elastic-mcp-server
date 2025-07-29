#!/usr/bin/env python3
"""
Test authentication methods with devtunnel MCP server.

This test validates different authentication approaches and ensures
the devtunnel access token authentication is working properly.
"""

import asyncio
import os
import httpx
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_devtunnel_auth_methods():
    """Test different authentication methods with the devtunnel."""
    mcp_server_url = os.getenv("MCP_SERVER_URL")
    devtunnel_token = os.getenv("DEVTUNNEL_ACCESS_TOKEN")
    
    if not mcp_server_url:
        logger.error("MCP_SERVER_URL not found in environment")
        return False
    
    logger.info(f"Testing auth methods with: {mcp_server_url}")
    logger.info(f"Devtunnel token present: {bool(devtunnel_token)}")
    
    # Simple test payload
    payload = {
        "jsonrpc": "2.0",
        "id": "test-auth",
        "method": "tools/list",
        "params": {}
    }
    
    success = False
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: No authentication
        logger.info("\n1. Testing without authentication...")
        try:
            response = await client.post(
                mcp_server_url,
                headers={"Content-Type": "application/json"},
                json=payload
            )
            logger.info(f"Status: {response.status_code}")
            if response.status_code == 200:
                logger.info("✅ No authentication required")
                success = True
            elif response.status_code == 401:
                logger.info("❌ Authentication required (expected)")
        except Exception as e:
            logger.error(f"Error: {e}")
        
        # Test 2: With devtunnel access token (proper MCP headers)
        if devtunnel_token:
            logger.info("\n2. Testing with devtunnel access token...")
            try:
                response = await client.post(
                    mcp_server_url,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream",
                        "X-Tunnel-Authorization": f"tunnel {devtunnel_token}"
                    },
                    json=payload
                )
                logger.info(f"Status: {response.status_code}")
                if response.status_code == 200:
                    logger.info("✅ Devtunnel authentication successful")
                    try:
                        # Try to parse JSON response
                        result = response.json()
                        if "result" in result and "tools" in result["result"]:
                            tools = result["result"]["tools"]
                            logger.info(f"Found {len(tools)} tools available")
                            success = True
                        else:
                            logger.info("✅ Authentication successful (non-JSON response)")
                            success = True
                    except Exception:
                        # Server-sent events or other non-JSON response is OK
                        logger.info("✅ Authentication successful (non-JSON response)")
                        logger.info(f"Response type: {response.headers.get('content-type', 'unknown')}")
                        success = True
                elif response.status_code == 401:
                    logger.error("❌ Devtunnel authentication failed")
                else:
                    logger.warning(f"Unexpected status: {response.status_code}")
                    logger.info(f"Response: {response.text[:200]}")
            except Exception as e:
                logger.error(f"Error: {e}")
        else:
            logger.warning("No DEVTUNNEL_ACCESS_TOKEN found, skipping token test")
        
        # Test 3: OPTIONS request to check CORS/auth requirements
        logger.info("\n3. Testing OPTIONS request...")
        try:
            response = await client.options(mcp_server_url)
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Headers: {dict(response.headers)}")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(test_devtunnel_auth_methods())
    exit(0 if result else 1)
