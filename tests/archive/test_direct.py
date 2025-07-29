#!/usr/bin/env python3
"""
Direct test of agent tool filtering
"""

import asyncio
import logging
from azure_ai_agent import AzureAIMCPAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Test agent tool filtering directly."""
    
    print("🔧 Direct Agent Tool Test")
    print("=" * 40)
    
    agent = AzureAIMCPAgent()
    
    try:
        # Initialize the agent properly
        print("Initializing agent...")
        await agent.initialize()
        
        print(f"Available MCP tools: {len(agent.mcp_tools)}")
        
        # Show available tools
        for tool in agent.mcp_tools:
            tool_name = tool['function']['name']
            print(f"  - {tool_name}")
        
        # Check filtering
        tool_names = [tool['function']['name'] for tool in agent.mcp_tools]
        print(f"\nTool filtering results:")
        print(f"  esql excluded: {'esql' not in tool_names}")
        print(f"  search included: {'search' in tool_names}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
