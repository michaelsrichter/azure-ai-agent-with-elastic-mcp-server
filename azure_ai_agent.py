"""
Azure AI Foundry Agent with MCP Server integration for Elasticsearch.
This agent can search and analyze data using Elasticsearch via an MCP server.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError

from config import config
from mcp_client import MCPClient, create_mcp_client
from elasticsearch_tools import ElasticsearchMCPTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AzureAIMCPAgent:
    """Azure AI Foundry Agent with MCP Server integration."""
    
    def __init__(self):
        """Initialize the Azure AI agent."""
        self.project_client: Optional[AIProjectClient] = None
        self.mcp_client: Optional[MCPClient] = None
        self.elasticsearch_tool: Optional[ElasticsearchMCPTool] = None
        self.agent_id: Optional[str] = None
        self.thread_id: Optional[str] = None
        self.mcp_tools: List[Dict[str, Any]] = []
        self.last_tool_outputs: List[Dict[str, Any]] = []  # Store last tool call outputs
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
    
    async def initialize(self):
        """Initialize the Azure AI client and MCP connection."""
        try:
            # Initialize Azure AI Project Client
            logger.info("Initializing Azure AI Project Client...")
            self.project_client = AIProjectClient(
                endpoint=config.project_endpoint,
                credential=DefaultAzureCredential()
            )
            
            # Initialize MCP Client
            logger.info("Initializing MCP Client...")
            self.mcp_client = await create_mcp_client()
            
            # Initialize Elasticsearch tool
            self.elasticsearch_tool = ElasticsearchMCPTool(self.mcp_client)
            
            # Get MCP tools and convert them for Azure AI
            await self._setup_mcp_tools()
            
            # Test MCP connection
            await self._test_mcp_connection()
            
            logger.info("Agent initialization completed successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    async def _setup_mcp_tools(self):
        """Setup MCP tools for Azure AI agent."""
        try:
            # Get available tools from MCP server
            mcp_tools = await self.mcp_client.get_available_tools()
            
            # Filter out tools we don't want to use
            excluded_tools = {"esql"}  # Add tool names to exclude here
            filtered_tools = [tool for tool in mcp_tools if tool.get("name") not in excluded_tools]
            
            # Convert MCP tools to Azure AI format
            self.mcp_tools = []
            for tool in filtered_tools:
                azure_tool = self._convert_mcp_tool_to_azure_format(tool)
                self.mcp_tools.append(azure_tool)
                logger.info(f"Converted MCP tool: {tool.get('name', 'Unknown')}")
            
            # Log excluded tools
            excluded_tool_names = [tool.get("name") for tool in mcp_tools if tool.get("name") in excluded_tools]
            if excluded_tool_names:
                logger.info(f"Excluded MCP tools: {excluded_tool_names}")
            
        except Exception as e:
            logger.error(f"Error setting up MCP tools: {e}")
            raise
    
    def _convert_mcp_tool_to_azure_format(self, mcp_tool: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MCP tool definition to Azure AI tool format."""
        return {
            "type": "function",
            "function": {
                "name": mcp_tool.get("name", "unknown_tool"),
                "description": mcp_tool.get("description", ""),
                "parameters": mcp_tool.get("inputSchema", {
                    "type": "object",
                    "properties": {},
                    "required": []
                })
            }
        }
    
    async def _test_mcp_connection(self):
        """Test the MCP server connection."""
        try:
            tools = await self.mcp_client.get_available_tools()
            logger.info(f"MCP server connection successful. Available tools: {len(tools)}")
            for tool in tools:
                logger.info(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        except Exception as e:
            logger.warning(f"MCP server connection test failed: {e}")
            logger.warning("Agent will still work, but MCP tools may not be available")
    
    async def create_agent(self) -> str:
        """Create an Azure AI agent with MCP tools.
        
        Returns:
            Agent ID.
        """
        try:
            logger.info("Creating Azure AI agent...")
            
            # Create agent with MCP tools
            agent = self.project_client.agents.create_agent(
                model=config.model_deployment_name,
                name=config.agent_name,
                instructions=config.agent_instructions,
                tools=self.mcp_tools  # Use converted MCP tools
                # Note: removed tool_resources={} as it causes validation issues
            )
            
            self.agent_id = agent.id
            logger.info(f"Created agent with ID: {self.agent_id}")
            logger.info(f"Agent has {len(self.mcp_tools)} MCP tools available")
            
            return self.agent_id
        
        except AzureError as e:
            logger.error(f"Azure error creating agent: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating agent: {e}")
            raise
    
    async def create_thread(self) -> str:
        """Create a conversation thread.
        
        Returns:
            Thread ID.
        """
        try:
            logger.info("Creating conversation thread...")
            
            thread = self.project_client.agents.threads.create()
            self.thread_id = thread.id
            
            logger.info(f"Created thread with ID: {self.thread_id}")
            return self.thread_id
        
        except AzureError as e:
            logger.error(f"Azure error creating thread: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating thread: {e}")
            raise
    
    async def send_message(self, content: str, role: str = "user") -> str:
        """Send a message to the agent.
        
        Args:
            content: Message content.
            role: Message role (user/assistant).
            
        Returns:
            Message ID.
        """
        try:
            if not self.thread_id:
                raise ValueError("No thread created. Call create_thread() first.")
            
            logger.info(f"Sending message: {content[:100]}...")
            
            message = self.project_client.agents.messages.create(
                thread_id=self.thread_id,
                role=role,
                content=content
            )
            
            logger.info(f"Message sent with ID: {message['id']}")
            return message['id']
        
        except AzureError as e:
            logger.error(f"Azure error sending message: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            raise
    
    async def run_agent(self) -> Dict[str, Any]:
        """Run the agent to process messages with MCP tool handling.
        
        Returns:
            Run result with status and messages.
        """
        try:
            if not self.agent_id or not self.thread_id:
                raise ValueError("Agent and thread must be created first.")
            
            logger.info("Running agent...")
            
            # Create run
            run = self.project_client.agents.runs.create(
                thread_id=self.thread_id,
                agent_id=self.agent_id
            )
            
            # Process run with MCP tool handling
            while True:
                # Check run status
                run = self.project_client.agents.runs.get(
                    thread_id=self.thread_id,
                    run_id=run.id
                )
                
                logger.info(f"Run status: {run.status}")
                
                if run.status == "completed":
                    break
                elif run.status == "requires_action":
                    # Handle MCP tool calls
                    await self._handle_mcp_tool_calls(run)
                elif run.status == "failed":
                    logger.error(f"Run failed: {run.last_error}")
                    return {
                        "status": "failed",
                        "error": run.last_error,
                        "messages": []
                    }
                elif run.status in ["cancelled", "expired"]:
                    logger.warning(f"Run {run.status}")
                    return {
                        "status": run.status,
                        "messages": await self.get_messages()
                    }
                
                # Wait a bit before checking again
                await asyncio.sleep(1)
            
            logger.info(f"Run completed with status: {run.status}")
            
            # Get messages from the thread
            messages = await self.get_messages()
            
            return {
                "status": run.status,
                "messages": messages,
                "run_id": run.id
            }
        
        except AzureError as e:
            logger.error(f"Azure error running agent: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error running agent: {e}")
            raise
    
    async def _handle_mcp_tool_calls(self, run):
        """Handle MCP tool calls during agent execution.
        
        Args:
            run: The run object that requires action.
        """
        try:
            logger.info("Handling MCP tool calls...")
            
            tool_outputs = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                
                logger.info(f"Executing MCP tool: {tool_name} with args: {arguments}")
                
                # Call MCP server directly
                try:
                    result = await self.mcp_client.call_tool(tool_name, arguments)
                    output = json.dumps(result) if isinstance(result, dict) else str(result)
                    logger.info(f"MCP tool {tool_name} executed successfully")
                except Exception as e:
                    logger.error(f"Error executing MCP tool {tool_name}: {e}")
                    output = json.dumps({
                        "error": f"Tool execution failed: {str(e)}",
                        "success": False
                    })
                
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": output
                })
            
            # Store the tool outputs for debugging/testing purposes
            self.last_tool_outputs = []
            for i, tool_call in enumerate(run.required_action.submit_tool_outputs.tool_calls):
                self.last_tool_outputs.append({
                    "tool_name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                    "output": tool_outputs[i]["output"]
                })
            
            # Submit tool outputs to Azure AI
            self.project_client.agents.runs.submit_tool_outputs(
                thread_id=self.thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
            
            logger.info("MCP tool outputs submitted successfully")
        
        except Exception as e:
            logger.error(f"Error handling MCP tool calls: {e}")
            raise
    
    async def handle_tool_calls(self, run_id: str):
        """Legacy method - kept for compatibility."""
        logger.warning("handle_tool_calls is deprecated. Use _handle_mcp_tool_calls instead.")
        run = self.project_client.agents.runs.get(
            thread_id=self.thread_id,
            run_id=run_id
        )
        if run.status == "requires_action":
            await self._handle_mcp_tool_calls(run)
    
    async def get_messages(self) -> list:
        """Get all messages from the current thread.
        
        Returns:
            List of messages.
        """
        try:
            if not self.thread_id:
                return []
            
            messages = self.project_client.agents.messages.list(
                thread_id=self.thread_id
            )
            
            formatted_messages = []
            for message in messages:
                formatted_messages.append({
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "created_at": getattr(message, 'created_at', None)
                })
            
            return formatted_messages
        
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    async def search_elasticsearch(self, query: str, index: str = None, size: int = 10) -> Dict[str, Any]:
        """Direct search in Elasticsearch via MCP server.
        
        Args:
            query: Search query.
            index: Elasticsearch index.
            size: Number of results.
            
        Returns:
            Search results.
        """
        try:
            result = await self.mcp_client.search_elasticsearch(query, index, size)
            return result
        except Exception as e:
            logger.error(f"Error in direct Elasticsearch search: {e}")
            return {"error": str(e), "success": False}
    
    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available MCP tools.
        
        Returns:
            List of available tools.
        """
        try:
            return await self.mcp_client.get_available_tools()
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return []
    
    async def cleanup(self):
        """Clean up resources."""
        try:
            if self.agent_id and self.project_client:
                logger.info("Cleaning up agent...")
                self.project_client.agents.delete_agent(self.agent_id)
                logger.info("Agent deleted successfully")
            
            if self.mcp_client:
                await self.mcp_client.__aexit__(None, None, None)
        
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")


async def main():
    """Main function to demonstrate the agent with direct MCP communication."""
    try:
        async with AzureAIMCPAgent() as agent:
            # List available tools
            tools = await agent.list_available_tools()
            print(f"Available MCP tools: {[tool.get('name') for tool in tools]}")
            
            # Create agent and thread
            agent_id = await agent.create_agent()
            thread_id = await agent.create_thread()
            
            # Example interaction
            await agent.send_message(
                "Can you search for documents containing 'machine learning' in Elasticsearch? "
                "Please show me the top 5 results and explain what you found."
            )
            
            # Run the agent with direct MCP communication
            result = await agent.run_agent()
            
            # Display results
            print(f"\nAgent Run Status: {result['status']}")
            print("\nConversation:")
            for message in reversed(result['messages']):
                print(f"{message['role'].upper()}: {message['content']}")
                print("-" * 50)
    
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())