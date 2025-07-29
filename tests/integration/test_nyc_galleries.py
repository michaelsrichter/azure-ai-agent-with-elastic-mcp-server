#!/usr/bin/env python3
"""
Test NYC Art Galleries search functionality.

This test validates searching the nyc-art-galleries index
with various query patterns.
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


async def test_nyc_galleries_search():
    """Test searching the NYC art galleries index."""
    
    print("🎨 Testing NYC Art Galleries Search")
    print("=" * 50)
    
    try:
        async with AzureAIMCPAgent() as agent:
            # Create agent and thread
            await agent.create_agent()
            await agent.create_thread()
            
            print(f"✅ Agent ready with {len(agent.mcp_tools)} tools")
            
            # Search for art galleries
            query = """
            Search the "nyc-art-galleries" index for galleries. 
            Show me 3 example galleries with their names and contact information.
            Use the search tool to find this information.
            """
            
            print(f"\nSending NYC galleries search request...")
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
                    print(f"\n🎨 NYC Galleries Response:")
                    print("-" * 50)
                    print(response[:800] + "..." if len(response) > 800 else response)
                    print("-" * 50)
                    
                    # Check for expected content
                    if 'gallery' in response.lower() or 'galleries' in response.lower():
                        print("✅ Response contains gallery information")
                        return True
                    else:
                        print("⚠️  Response may not contain gallery information")
                        return False
                else:
                    print("❌ No response content found")
                    return False
            else:
                print("❌ No messages found")
                return False
                
    except Exception as e:
        print(f"❌ NYC galleries search failed: {e}")
        logger.exception("NYC galleries search test failed")
        return False


async def test_specific_gallery_search():
    """Test searching for specific gallery types or locations."""
    
    print("\n🔍 Testing Specific Gallery Search")
    print("=" * 50)
    
    try:
        async with AzureAIMCPAgent() as agent:
            # Create agent and thread
            await agent.create_agent()
            await agent.create_thread()
            
            # Search for specific type
            query = """
            Search the "nyc-art-galleries" index for galleries in Manhattan or Chelsea.
            Show me any matches with location information.
            Keep the response concise.
            """
            
            print(f"\nSending specific gallery search...")
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
                    print(f"\n🗽 Location-Based Search Response:")
                    print("-" * 50)
                    print(response[:600] + "..." if len(response) > 600 else response)
                    print("-" * 50)
                    return True
                else:
                    print("❌ No response content found")
                    return False
            else:
                print("❌ No messages found")
                return False
                
    except Exception as e:
        print(f"❌ Specific gallery search failed: {e}")
        logger.exception("Specific gallery search test failed")
        return False


async def run_all_tests():
    """Run all NYC galleries search tests."""
    print("🧪 NYC Art Galleries Tests")
    print("=" * 50)
    
    tests = [
        ("General Galleries Search", test_nyc_galleries_search),
        ("Specific Gallery Search", test_specific_gallery_search)
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
