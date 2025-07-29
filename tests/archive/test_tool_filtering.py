#!/usr/bin/env python3
"""
Simple test to verify the agent only uses the search tool and not esql
"""

import asyncio
import logging
from azure_ai_agent import AzureAIMCPAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_agent_tools():
    """Test that the agent only has access to the search tool (not esql)."""
    
    print("🔧 Testing Agent Tool Filtering")
    print("=" * 50)
    
    try:
        async with AzureAIMCPAgent() as agent:
            # Create agent
            await agent.create_agent()
            
            print(f"\n✅ Agent created successfully!")
            print(f"Available MCP tools: {len(agent.mcp_tools)}")
            
            # List the tools that are available
            for i, tool in enumerate(agent.mcp_tools, 1):
                tool_name = tool['function']['name']
                tool_desc = tool['function']['description']
                print(f"  {i}. {tool_name}: {tool_desc}")
            
            # Check if esql is excluded
            tool_names = [tool['function']['name'] for tool in agent.mcp_tools]
            if 'esql' in tool_names:
                print(f"\n❌ ERROR: esql tool is still present!")
            else:
                print(f"\n✅ SUCCESS: esql tool has been filtered out!")
            
            if 'search' in tool_names:
                print(f"✅ SUCCESS: search tool is available!")
            else:
                print(f"❌ ERROR: search tool is missing!")
            
    except Exception as e:
        logger.error(f"Error testing agent tools: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_agent_tools())
