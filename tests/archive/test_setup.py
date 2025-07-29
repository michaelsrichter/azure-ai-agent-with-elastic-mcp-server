"""
Test script to verify MCP server connection and Elasticsearch tools.
Run this to check if your MCP server is properly set up.
"""

import asyncio
import json
import logging
from mcp_client import create_mcp_client
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_connection():
    """Test basic MCP server connection."""
    print("Testing MCP server connection...")
    
    try:
        async with await create_mcp_client() as client:
            tools = await client.get_available_tools()
            
            if tools:
                print(f"✓ Connected to MCP server at {config.mcp_server_url}")
                print(f"✓ Found {len(tools)} available tools:")
                for tool in tools:
                    name = tool.get('name', 'Unknown')
                    description = tool.get('description', 'No description')[:100]
                    print(f"  - {name}: {description}")
                return True
            else:
                print(f"✗ No tools found on MCP server")
                return False
    
    except Exception as e:
        print(f"✗ Failed to connect to MCP server: {e}")
        return False


async def test_elasticsearch_search():
    """Test Elasticsearch search via MCP server."""
    print("\nTesting Elasticsearch search...")
    
    try:
        async with await create_mcp_client() as client:
            # Test search
            result = await client.search_elasticsearch(
                query="test",
                size=1
            )
            
            if "error" in result:
                print(f"✗ Elasticsearch search failed: {result['error']}")
                return False
            else:
                print("✓ Elasticsearch search successful")
                print(f"  Response keys: {list(result.keys())}")
                return True
    
    except Exception as e:
        print(f"✗ Elasticsearch search error: {e}")
        return False


async def test_elasticsearch_mapping():
    """Test Elasticsearch mapping retrieval via MCP server."""
    print("\nTesting Elasticsearch mapping...")
    
    try:
        async with await create_mcp_client() as client:
            result = await client.get_elasticsearch_mapping()
            
            if "error" in result:
                print(f"✗ Elasticsearch mapping failed: {result['error']}")
                return False
            else:
                print("✓ Elasticsearch mapping retrieval successful")
                return True
    
    except Exception as e:
        print(f"✗ Elasticsearch mapping error: {e}")
        return False


async def test_config_validation():
    """Test configuration validation."""
    print("\nTesting configuration...")
    
    try:
        print(f"✓ Project endpoint: {config.project_endpoint}")
        print(f"✓ Model deployment: {config.model_deployment_name}")
        print(f"✓ MCP server URL: {config.mcp_server_url}")
        print(f"✓ Elasticsearch host: {config.elasticsearch_host}:{config.elasticsearch_port}")
        print(f"✓ Elasticsearch index: {config.elasticsearch_index}")
        print(f"✓ Agent name: {config.agent_name}")
        return True
    
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


async def main():
    """Run all tests."""
    print("Azure AI Foundry Agent - MCP Server Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config_validation),
        ("MCP Connection", test_mcp_connection),
        ("Elasticsearch Search", test_elasticsearch_search),
        ("Elasticsearch Mapping", test_elasticsearch_mapping),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    
    all_passed = True
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {test_name}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your setup is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting tips:")
        print("1. Ensure your .env file is properly configured")
        print("2. Verify your MCP server is running at localhost:8080/mcp")
        print("3. Check that Elasticsearch is accessible from your MCP server")
        print("4. Confirm your Azure AI Foundry credentials are valid")


if __name__ == "__main__":
    asyncio.run(main())
