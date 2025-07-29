#!/usr/bin/env python3
"""
Test different authentication methods with the devtunnel
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
    if not mcp_server_url:
        logger.error("MCP_SERVER_URL not found in environment")
        return
    
    logger.info(f"Testing different auth methods with: {mcp_server_url}")
    
    # Simple test payload
    payload = {
        "jsonrpc": "2.0",
        "id": "test-001",
        "method": "tools/list",
        "params": {}
    }
    
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
            if response.status_code != 401:
                logger.info(f"Response: {response.text[:200]}")
        except Exception as e:
            logger.error(f"Error: {e}")
        
        # Test 2: Basic auth (common for tunnels)
        logger.info("\n2. Testing with basic auth (empty credentials)...")
        try:
            response = await client.post(
                mcp_server_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Basic "
                },
                json=payload
            )
            logger.info(f"Status: {response.status_code}")
            if response.status_code != 401:
                logger.info(f"Response: {response.text[:200]}")
        except Exception as e:
            logger.error(f"Error: {e}")
        
        # Test 3: Check for specific headers that might be required
        logger.info("\n3. Testing with devtunnel-specific headers...")
        try:
            response = await client.post(
                mcp_server_url,
                headers={
                    "Content-Type": "application/json",
                    "X-Forwarded-Proto": "https",
                    "X-Original-Host": mcp_server_url.split("//")[1].split("/")[0]
                },
                json=payload
            )
            logger.info(f"Status: {response.status_code}")
            if response.status_code != 401:
                logger.info(f"Response: {response.text[:200]}")
        except Exception as e:
            logger.error(f"Error: {e}")
        
        # Test 4: OPTIONS request to check CORS/auth requirements
        logger.info("\n4. Testing OPTIONS request...")
        try:
            response = await client.options(mcp_server_url)
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Headers: {dict(response.headers)}")
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_devtunnel_auth_methods())
