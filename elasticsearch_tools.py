"""
Custom tools for Azure AI Foundry Agent to interact with MCP server.
These tools allow the agent to search Elasticsearch via the MCP server.
"""

import json
import logging
from typing import Dict, Any, List
from mcp_client import MCPClient

logger = logging.getLogger(__name__)


class ElasticsearchMCPTool:
    """Tool for searching Elasticsearch via MCP server."""
    
    def __init__(self, mcp_client: MCPClient):
        """Initialize the Elasticsearch MCP tool.
        
        Args:
            mcp_client: Instance of MCPClient for server communication.
        """
        self.mcp_client = mcp_client
    
    @property
    def search_tool_definition(self) -> Dict[str, Any]:
        """Get the search tool definition for Azure AI agent."""
        return {
            "type": "function",
            "function": {
                "name": "elasticsearch_search",
                "description": "Search for documents in Elasticsearch using the MCP server. "
                              "This tool can find relevant documents based on text queries, "
                              "filters, and other search criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to execute against Elasticsearch. "
                                         "Can be a simple text search or a more complex query."
                        },
                        "index": {
                            "type": "string",
                            "description": "The Elasticsearch index to search in. "
                                         "If not provided, uses the default configured index."
                        },
                        "size": {
                            "type": "integer",
                            "description": "Number of search results to return. Default is 10.",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional filters to apply to the search query. "
                                         "Should be a valid Elasticsearch filter object."
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    @property
    def mapping_tool_definition(self) -> Dict[str, Any]:
        """Get the mapping tool definition for Azure AI agent."""
        return {
            "type": "function",
            "function": {
                "name": "elasticsearch_mapping",
                "description": "Get the field mapping information for an Elasticsearch index. "
                              "This helps understand the structure and data types of documents "
                              "in the index.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "index": {
                            "type": "string",
                            "description": "The Elasticsearch index to get mapping information for. "
                                         "If not provided, uses the default configured index."
                        }
                    },
                    "required": []
                }
            }
        }
    
    @property
    def analyze_tool_definition(self) -> Dict[str, Any]:
        """Get the analyze tool definition for Azure AI agent."""
        return {
            "type": "function",
            "function": {
                "name": "elasticsearch_analyze",
                "description": "Analyze text using Elasticsearch analyzers to understand "
                              "how text will be processed for search.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to analyze."
                        },
                        "analyzer": {
                            "type": "string",
                            "description": "The analyzer to use. If not provided, uses the default analyzer.",
                            "default": "standard"
                        },
                        "index": {
                            "type": "string",
                            "description": "The index to use for analysis context."
                        }
                    },
                    "required": ["text"]
                }
            }
        }
    
    async def execute_search(self, arguments: Dict[str, Any]) -> str:
        """Execute an Elasticsearch search via MCP server.
        
        Args:
            arguments: Search arguments from the agent.
            
        Returns:
            JSON string with search results.
        """
        try:
            # Extract arguments
            query = arguments.get("query", "")
            index = arguments.get("index")
            size = arguments.get("size", 10)
            filters = arguments.get("filters")
            
            # Prepare search arguments for MCP server
            search_args = {
                "query": query,
                "size": size
            }
            
            if index:
                search_args["index"] = index
            
            if filters:
                search_args["filters"] = filters
            
            # Execute search via MCP client
            result = await self.mcp_client.call_tool("elasticsearch_search", search_args)
            
            # Format result for agent
            if "error" in result:
                return json.dumps({
                    "success": False,
                    "error": result["error"],
                    "message": "Failed to execute Elasticsearch search"
                })
            
            return json.dumps({
                "success": True,
                "results": result,
                "query": query,
                "total_hits": result.get("hits", {}).get("total", {}).get("value", 0) if "hits" in result else 0
            })
        
        except Exception as e:
            logger.error(f"Error executing Elasticsearch search: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "Unexpected error during search execution"
            })
    
    async def execute_mapping(self, arguments: Dict[str, Any]) -> str:
        """Get Elasticsearch index mapping via MCP server.
        
        Args:
            arguments: Mapping arguments from the agent.
            
        Returns:
            JSON string with mapping information.
        """
        try:
            index = arguments.get("index")
            
            mapping_args = {}
            if index:
                mapping_args["index"] = index
            
            result = await self.mcp_client.call_tool("elasticsearch_mapping", mapping_args)
            
            if "error" in result:
                return json.dumps({
                    "success": False,
                    "error": result["error"],
                    "message": "Failed to get Elasticsearch mapping"
                })
            
            return json.dumps({
                "success": True,
                "mapping": result,
                "index": index or "default"
            })
        
        except Exception as e:
            logger.error(f"Error getting Elasticsearch mapping: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "Unexpected error getting mapping"
            })
    
    async def execute_analyze(self, arguments: Dict[str, Any]) -> str:
        """Analyze text using Elasticsearch via MCP server.
        
        Args:
            arguments: Analyze arguments from the agent.
            
        Returns:
            JSON string with analysis results.
        """
        try:
            text = arguments.get("text", "")
            analyzer = arguments.get("analyzer", "standard")
            index = arguments.get("index")
            
            analyze_args = {
                "text": text,
                "analyzer": analyzer
            }
            
            if index:
                analyze_args["index"] = index
            
            result = await self.mcp_client.call_tool("elasticsearch_analyze", analyze_args)
            
            if "error" in result:
                return json.dumps({
                    "success": False,
                    "error": result["error"],
                    "message": "Failed to analyze text"
                })
            
            return json.dumps({
                "success": True,
                "analysis": result,
                "text": text,
                "analyzer": analyzer
            })
        
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "Unexpected error during text analysis"
            })


def get_elasticsearch_tools(mcp_client: MCPClient) -> List[Dict[str, Any]]:
    """Get all Elasticsearch tools for the Azure AI agent.
    
    Args:
        mcp_client: Instance of MCPClient.
        
    Returns:
        List of tool definitions.
    """
    tool = ElasticsearchMCPTool(mcp_client)
    return [
        tool.search_tool_definition,
        tool.mapping_tool_definition,
        tool.analyze_tool_definition
    ]
