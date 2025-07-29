#!/usr/bin/env python3
"""
Test script to demonstrate Azure AI agent searching the nyc-art-galleries index
using the MCP server's search tool.
"""

import asyncio
import logging
from azure_ai_agent import AzureAIMCPAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_nyc_galleries_search():
    """Test searching the nyc-art-galleries index through the Azure AI agent."""
    
    print("🎨 Testing NYC Art Galleries Search")
    print("=" * 60)
    
    # Initialize the agent
    print("\n1. Initializing Azure AI Agent...")
    
    try:
        async with AzureAIMCPAgent() as agent:
            # Create agent and thread
            await agent.create_agent()
            await agent.create_thread()
            
            # Ask the agent to search the nyc-art-galleries index
            search_query = """
            Can you search the "nyc-art-galleries" index in Elasticsearch? 
            Please show me:
            1. A few example documents from this index
            2. What fields are available in the documents
            3. Maybe search for galleries in Manhattan or Brooklyn
            
            Use the search tool to query this specific index.
            """
            
            print(f"\n2. Sending search request...")
            print(f"Query: {search_query.strip()}")
            
            # Send the message and run the agent
            await agent.send_message(search_query)
            result = await agent.run_agent()
            
            print(f"\n3. Agent Response:")
            print("-" * 40)
            
            # Get the messages to see the conversation
            messages = await agent.get_messages()
            for i, msg in enumerate(messages[-2:], 1):  # Show last 2 messages (user + assistant)
                role = msg.get('role', 'unknown')
                content = msg.get('content', [])
                if content and isinstance(content, list) and len(content) > 0:
                    text_content = content[0].get('text', {}).get('value', 'No content')
                    print(f"{i}. {role.upper()}: {text_content[:500]}...")
            print("-" * 40)
        
    except Exception as e:
        logger.error(f"Error during search test: {e}")
        raise
    
    print(f"\n✅ NYC Art Galleries search test completed!")

async def test_specific_search_queries():
    """Test specific search queries on the nyc-art-galleries index."""
    
    print("\n🔍 Testing Specific Search Queries")
    print("=" * 60)
    
    try:
        async with AzureAIMCPAgent() as agent:
            # Create agent and thread
            await agent.create_agent()
            await agent.create_thread()
            
            # Test different search patterns
            queries = [
                {
                    "name": "Basic Match All",
                    "query": """Search the nyc-art-galleries index with a simple match_all query to show me 3 example documents."""
                },
                {
                    "name": "Manhattan Galleries", 
                    "query": """Search the nyc-art-galleries index for galleries located in Manhattan. Show me the names and addresses."""
                },
                {
                    "name": "Gallery by Name",
                    "query": """Search the nyc-art-galleries index for any gallery with 'museum' in the name."""
                }
            ]
            
            for i, test_case in enumerate(queries, 1):
                print(f"\n{i}. {test_case['name']}")
                print(f"   Query: {test_case['query']}")
                
                try:
                    await agent.send_message(test_case['query'])
                    result = await agent.run_agent()
                    
                    # Get the assistant's response
                    messages = await agent.get_messages()
                    if messages:
                        last_msg = messages[-1]
                        content = last_msg.get('content', [])
                        if content and isinstance(content, list) and len(content) > 0:
                            response = content[0].get('text', {}).get('value', 'No response')
                            print(f"   Response: {response[:200]}..." if len(response) > 200 else f"   Response: {response}")
                        else:
                            print(f"   Response: No content in message")
                    else:
                        print(f"   Response: No messages found")
                except Exception as e:
                    print(f"   Error: {e}")
                
                print()
        
    except Exception as e:
        logger.error(f"Error during specific search tests: {e}")
        raise
    
    print(f"✅ Specific search tests completed!")

if __name__ == "__main__":
    print("🚀 Starting NYC Art Galleries Search Tests")
    print("=" * 60)
    
    # Run the basic search test
    asyncio.run(test_nyc_galleries_search())
    
    print("\n" + "=" * 60)
    
    # Run specific search queries
    asyncio.run(test_specific_search_queries())
    
    print("\n🎉 All NYC Art Galleries tests completed!")
