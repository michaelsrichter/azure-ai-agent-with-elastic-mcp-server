#!/usr/bin/env python3
"""
Test Azure AI Agent with tool filtering.

This test validates that the agent correctly filters out the esql tool
and only uses search and supporting tools.
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from azure_ai_agent import AzureAIMCPAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_tool_filtering():
    """Test that the agent only has access to filtered tools (no esql)."""
    
    print("🔧 Testing Agent Tool Filtering")
    print("=" * 50)
    
    try:
        async with AzureAIMCPAgent() as agent:
            # Create agent
            await agent.create_agent()
            
            print(f"\n✅ Agent created successfully!")
            print(f"Available MCP tools: {len(agent.mcp_tools)}")
            
            # Check that esql is not in the tools
            tool_names = []
            for tool in agent.mcp_tools:
                tool_name = tool['function']['name']
                tool_names.append(tool_name)
                print(f"  ✓ {tool_name}")
            
            # Verify esql is excluded
            if 'esql' in tool_names:
                print(f"\n❌ ERROR: esql tool should be filtered out!")
                return False
            else:
                print(f"\n✅ SUCCESS: esql tool correctly filtered out")
            
            # Verify expected tools are present
            expected_tools = ['search', 'list_indices', 'get_mappings', 'get_shards']
            missing_tools = []
            
            for expected in expected_tools:
                if expected not in tool_names:
                    missing_tools.append(expected)
            
            if missing_tools:
                print(f"⚠️  Missing expected tools: {missing_tools}")
            else:
                print(f"✅ All expected tools present: {expected_tools}")
            
            return len(missing_tools) == 0
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Tool filtering test failed")
        return False


async def test_search_only_functionality():
    """Test that the agent can search without using esql."""
    
    print("\n🔍 Testing Search-Only Functionality")
    print("=" * 50)
    
    try:
        async with AzureAIMCPAgent() as agent:
            # Create agent and thread
            await agent.create_agent()
            await agent.create_thread()
            
            print(f"✅ Agent and thread created")
            
            # Simple search request that should use search tool only
            query = """
            Search the index and show me 2 example documents. 
            Use only the search tool - do not use ES|QL queries.
            Be brief in your response.
            """
            
            print(f"\nSending search request...")
            await agent.send_message(query)
            
            print(f"Running agent...")
            await agent.run_agent()
            
            # Get the response
            messages = await agent.get_messages()
            if messages:
                last_msg = messages[-1]
                content = last_msg.get('content', [])
                if content and isinstance(content, list) and len(content) > 0:
                    response = content[0].get('text', {}).get('value', 'No response')
                    print(f"\n📋 Agent Response (truncated):")
                    print("-" * 40)
                    print(response[:400] + "..." if len(response) > 400 else response)
                    print("-" * 40)
                    
                    # Check that response doesn't mention esql errors
                    if 'esql' in response.lower() and 'error' in response.lower():
                        print("⚠️  Response contains esql error mention")
                        return False
                    else:
                        print("✅ Response looks good - no esql errors")
                        return True
                else:
                    print("❌ No response content found")
                    return False
            else:
                print("❌ No messages found")
                return False
                
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        logger.exception("Search functionality test failed")
        return False


async def run_all_tests():
    """Run all tool filtering tests."""
    print("🧪 Tool Filtering Tests")
    print("=" * 50)
    
    tests = [
        ("Tool Filtering", test_tool_filtering),
        ("Search-Only Functionality", test_search_only_functionality)
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
