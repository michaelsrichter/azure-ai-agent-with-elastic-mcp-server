#!/usr/bin/env python3
"""
Test MCP server connection and basic functionality.

This test verifies that the MCP server is accessible and
that Elasticsearch tools are working correctly.
"""

import asyncio
import json
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mcp_client import create_mcp_client
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_connection():
    """Test basic MCP server connection."""
    print("🔗 Testing MCP server connection...")
    
    try:
        async with await create_mcp_client() as client:
            tools = await client.get_available_tools()
            
            if tools:
                print(f"✅ Connected to MCP server at {config.mcp_server_url}")
                print(f"✅ Found {len(tools)} available tools:")
                for tool in tools:
                    name = tool.get('name', 'Unknown')
                    description = tool.get('description', 'No description')[:100]
                    print(f"  - {name}: {description}")
                return True
            else:
                print(f"❌ No tools found on MCP server")
                return False
    
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        return False


async def test_elasticsearch_list_indices():
    """Test Elasticsearch list indices via MCP server."""
    print("\n📋 Testing Elasticsearch list indices...")
    
    try:
        async with await create_mcp_client() as client:
            result = await client.call_tool("list_indices", {})
            
            if result and result.get('status') == 'success':
                indices = result.get('data', [])
                print(f"✅ Found {len(indices)} indices")
                
                # Look for our target index
                target_index = config.elasticsearch_index
                found_target = any(idx.get('name') == target_index for idx in indices)
                
                if found_target:
                    print(f"✅ Target index '{target_index}' found")
                else:
                    print(f"⚠️  Target index '{target_index}' not found")
                    print("Available indices:")
                    for idx in indices[:5]:  # Show first 5
                        print(f"  - {idx.get('name', 'Unknown')}")
                
                return True
            else:
                print(f"❌ Failed to list indices: {result}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to list indices: {e}")
        return False


async def test_elasticsearch_search():
    """Test Elasticsearch search via MCP server."""
    print("\n🔍 Testing Elasticsearch search...")
    
    try:
        async with await create_mcp_client() as client:
            # Test simple search
            search_params = {
                "query_body": {
                    "query": {"match_all": {}},
                    "size": 3
                }
            }
            
            result = await client.call_tool("search", search_params)
            
            if result and result.get('status') == 'success':
                hits = result.get('data', {}).get('hits', {})
                total = hits.get('total', {}).get('value', 0)
                documents = hits.get('hits', [])
                
                print(f"✅ Search successful: {total} total documents")
                print(f"✅ Retrieved {len(documents)} sample documents")
                
                if documents:
                    first_doc = documents[0]
                    source = first_doc.get('_source', {})
                    print(f"✅ Sample document fields: {list(source.keys())}")
                
                return True
            else:
                print(f"❌ Search failed: {result}")
                return False
                
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False


async def run_all_tests():
    """Run all setup tests."""
    print("🧪 MCP Agent Setup Tests")
    print("=" * 50)
    
    tests = [
        ("MCP Connection", test_mcp_connection),
        ("List Indices", test_elasticsearch_list_indices),
        ("Search Test", test_elasticsearch_search)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    return all_passed


if __name__ == "__main__":
    result = asyncio.run(run_all_tests())
    exit(0 if result else 1)
