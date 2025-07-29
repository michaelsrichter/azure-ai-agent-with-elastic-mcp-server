"""
Example usage of the Azure AI Foundry Agent with MCP Server.
This script demonstrates how to use the agent to search Elasticsearch.
"""

import asyncio
import logging
from azure_ai_agent import AzureAIMCPAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_search():
    """Example: Basic Elasticsearch search via the agent."""
    print("=== Example: Basic Search ===")
    
    async with AzureAIMCPAgent() as agent:
        # Create agent and thread
        await agent.create_agent()
        await agent.create_thread()
        
        # Send a search request
        await agent.send_message(
            "Search for documents containing 'python programming' in Elasticsearch. "
            "Show me the top 3 results with their titles and summaries."
        )
        
        # Run the agent and get response
        result = await agent.run_agent()
        
        # Display conversation
        print("\nConversation:")
        for message in reversed(result['messages']):
            print(f"\n{message['role'].upper()}:")
            print(message['content'])


async def example_filtered_search():
    """Example: Filtered search with specific criteria."""
    print("\n=== Example: Filtered Search ===")
    
    async with AzureAIMCPAgent() as agent:
        # Create agent and thread
        await agent.create_agent()
        await agent.create_thread()
        
        # Send a filtered search request
        await agent.send_message(
            "I need to search for documents about 'machine learning' that were "
            "published in the last year. Can you help me find the most relevant ones? "
            "Please also show me the document structure by getting the index mapping first."
        )
        
        # Run the agent and get response
        result = await agent.run_agent()
        
        # Display conversation
        print("\nConversation:")
        for message in reversed(result['messages']):
            print(f"\n{message['role'].upper()}:")
            print(message['content'])


async def example_direct_mcp_search():
    """Example: Direct search using MCP client (without agent)."""
    print("\n=== Example: Direct MCP Search ===")
    
    async with AzureAIMCPAgent() as agent:
        # Initialize just to get MCP client
        await agent.initialize()
        
        # Direct search via MCP
        result = await agent.search_elasticsearch(
            query="artificial intelligence",
            size=5
        )
        
        print(f"Direct search result: {result}")


async def example_conversation():
    """Example: Multi-turn conversation with the agent."""
    print("\n=== Example: Multi-turn Conversation ===")
    
    async with AzureAIMCPAgent() as agent:
        # Create agent and thread
        await agent.create_agent()
        await agent.create_thread()
        
        # First message
        print("\nUser: What's in my Elasticsearch index?")
        await agent.send_message("What's in my Elasticsearch index? Can you show me the mapping and some sample documents?")
        result = await agent.run_agent()
        
        print(f"Agent: {result['messages'][0]['content']}")
        
        # Follow-up message
        print("\nUser: Now search for documents about 'data science'")
        await agent.send_message("Now search for documents about 'data science' and summarize what you find.")
        result = await agent.run_agent()
        
        print(f"Agent: {result['messages'][0]['content']}")


async def main():
    """Run all examples."""
    try:
        print("Azure AI Foundry Agent with MCP Server Examples")
        print("=" * 50)
        
        # Run examples
        await example_basic_search()
        await example_filtered_search()
        await example_direct_mcp_search()
        await example_conversation()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
    
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        print(f"\nError: {e}")
        print("\nPlease ensure:")
        print("1. Your .env file is configured with valid Azure AI Foundry credentials")
        print("2. Your MCP server is running at localhost:8080/mcp")
        print("3. Your Elasticsearch instance is accessible from the MCP server")


if __name__ == "__main__":
    asyncio.run(main())
