#!/usr/bin/env python3
"""
Test the agent with filtered tools (search only, no esql) on nyc-art-galleries
"""

import asyncio
import logging
from azure_ai_agent import AzureAIMCPAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_search_only():
    """Test that the agent can search nyc-art-galleries without using esql."""
    
    print("🔍 Testing Search-Only Agent")
    print("=" * 50)
    
    try:
        async with AzureAIMCPAgent() as agent:
            # Create agent and thread
            await agent.create_agent()
            await agent.create_thread()
            
            print(f"\n✅ Agent created with {len(agent.mcp_tools)} tools (esql excluded)")
            
            # Simple search request
            query = """
            Search the "nyc-art-galleries" index and show me 3 example documents. 
            Use only the search tool - do not use ES|QL queries.
            """
            
            print(f"\nSending search request...")
            await agent.send_message(query)
            
            print(f"Running agent (with search tool only)...")
            await agent.run_agent()
            
            # Get the response
            messages = await agent.get_messages()
            if messages:
                last_msg = messages[-1]
                content = last_msg.get('content', [])
                if content and isinstance(content, list) and len(content) > 0:
                    response = content[0].get('text', {}).get('value', 'No response')
                    print(f"\n📋 Agent Response:")
                    print("-" * 40)
                    print(response[:800] + "..." if len(response) > 800 else response)
                    print("-" * 40)
                else:
                    print(f"No content in response")
            
    except Exception as e:
        logger.error(f"Error during search test: {e}")
        raise
    
    print(f"\n✅ Search-only test completed!")

if __name__ == "__main__":
    asyncio.run(test_search_only())
