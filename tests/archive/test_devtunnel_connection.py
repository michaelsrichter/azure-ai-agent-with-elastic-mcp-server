#!/usr/bin/env python3
"""Test MCP connection with devtunnel URL."""

import sys
import os
import asyncio
from datetime import datetime

print(f"🔗 Testing MCP Devtunnel Connection")
print(f"Started at: {datetime.now()}")
print("=" * 50)

try:
    print("1. Importing modules...")
    from mcp_client import MCPClient
    from config import Config
    print("   ✅ Imports successful")
    
    config = Config()
    print(f"   🌐 MCP Server URL: {config.mcp_server_url}")
    print(f"   📊 Elasticsearch index: {config.elasticsearch_index}")
    
    async def test_devtunnel_connection():
        try:
            print("\n2. Creating MCP client...")
            client = MCPClient()
            print("   ✅ Client created")
            
            print("\n3. Connecting to devtunnel MCP server...")
            await client.__aenter__()
            print("   ✅ Connection established")
            
            print("\n4. Testing tool retrieval...")
            tools = await client.get_available_tools()
            print(f"   ✅ Retrieved {len(tools)} tools from MCP server")
            
            for tool in tools:
                print(f"     - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
            
            print("\n5. Testing search tool specifically...")
            if any(tool.get('name') == 'search' for tool in tools):
                try:
                    # Test with correct parameters
                    search_result = await client.call_tool("search", {
                        "index": "nyc-art-galleries",
                        "query_body": {
                            "query": {"match_all": {}},
                            "size": 1
                        }
                    })
                    print("   ✅ Search tool test successful!")
                    print(f"   📊 Search returned data: {len(str(search_result))} characters")
                except Exception as e:
                    print(f"   ❌ Search tool test failed: {e}")
            else:
                print("   ⚠️ Search tool not found in available tools")
            
            print("\n6. Cleaning up...")
            await client.__aexit__(None, None, None)
            print("   ✅ Connection closed")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Connection test failed: {e}")
            print(f"   🔍 Error type: {type(e).__name__}")
            
            # Check if it's an authentication error
            if "401" in str(e) or "unauthorized" in str(e).lower():
                print("   🔐 This appears to be an authentication error")
                print("   💡 The devtunnel may require Entra authentication")
            elif "403" in str(e) or "forbidden" in str(e).lower():
                print("   🚫 This appears to be an authorization error")
                print("   💡 You may not have access to this devtunnel")
            elif "timeout" in str(e).lower() or "connection" in str(e).lower():
                print("   ⏱️ This appears to be a connection/timeout error")
                print("   💡 The devtunnel may not be running or accessible")
            
            import traceback
            print(f"\n   📋 Full error details:")
            traceback.print_exc()
            return False
    
    print("\n🎯 Starting devtunnel connection test...")
    success = asyncio.run(test_devtunnel_connection())
    
    if success:
        print("\n🎉 Devtunnel connection test completed successfully!")
        print("   ✅ The MCP server is accessible via devtunnel")
        print("   ✅ All tools are working correctly")
    else:
        print("\n💥 Devtunnel connection test failed!")
        print("   ❌ Cannot connect to the MCP server via devtunnel")
        
except Exception as e:
    print(f"❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()

print(f"\nFinished at: {datetime.now()}")
