#!/usr/bin/env python3
"""
Debug script to test the MCP server's search tool directly.
"""

import asyncio
import json
from mcp_client import MCPClient

async def test_search_tool_directly():
    """Test the MCP server's search tool directly to understand its parameters."""
    
    print("🔍 Testing MCP Search Tool Directly")
    print("=" * 50)
    
    async with MCPClient("http://localhost:8080/mcp") as client:
        try:
            # Get available tools first
            print("1. Getting available tools...")
            tools = await client.get_available_tools()
            
            # Find the search tool
            search_tool = None
            for tool in tools:
                if tool['name'] == 'search':
                    search_tool = tool
                    break
            
            if search_tool:
                print(f"\n2. Search tool found:")
                print(f"   Name: {search_tool['name']}")
                print(f"   Description: {search_tool['description']}")
                print(f"   Schema: {json.dumps(search_tool.get('inputSchema', {}), indent=4)}")
            else:
                print("❌ Search tool not found!")
                return
            
            # Test different search parameters
            test_cases = [
                {
                    "name": "Basic search with match_all",
                    "params": {
                        "index": "nyc-art-galleries",
                        "query_body": {
                            "query": {
                                "match_all": {}
                            }
                        }
                    }
                },
                {
                    "name": "Search with size limit",
                    "params": {
                        "index": "nyc-art-galleries",
                        "query_body": {
                            "query": {
                                "match_all": {}
                            },
                            "size": 3
                        }
                    }
                },
                {
                    "name": "Search with specific fields",
                    "params": {
                        "index": "nyc-art-galleries",
                        "query_body": {
                            "query": {
                                "match_all": {}
                            },
                            "size": 3
                        },
                        "fields": ["name", "contact"]
                    }
                }
            ]
            
            for i, test_case in enumerate(test_cases, 3):
                print(f"\n{i}. {test_case['name']}")
                print(f"   Parameters: {json.dumps(test_case['params'], indent=4)}")
                
                try:
                    result = await client.call_tool("search", test_case['params'])
                    print(f"   ✅ Success! Response length: {len(str(result))}")
                    if 'content' in result:
                        content = result['content']
                        if len(content) > 200:
                            print(f"   Response preview: {content[:200]}...")
                        else:
                            print(f"   Response: {content}")
                    else:
                        print(f"   Full response: {result}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
        except Exception as e:
            print(f"❌ Error testing search tool: {e}")

if __name__ == "__main__":
    asyncio.run(test_search_tool_directly())
