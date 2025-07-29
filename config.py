"""
Configuration module for Azure AI Foundry Agent with MCP Server integration.
Handles environment variables and configuration validation.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field, validator
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Config(BaseSettings):
    """Configuration settings for the Azure AI Foundry Agent."""
    
    # Azure AI Foundry Configuration
    project_endpoint: str = Field(..., env="PROJECT_ENDPOINT")
    model_deployment_name: str = Field(..., env="MODEL_DEPLOYMENT_NAME")
    
    # MCP Server Configuration
    mcp_server_url: str = Field(default="http://localhost:8080/mcp", env="MCP_SERVER_URL")
    
    # DevTunnel Authentication (optional)
    devtunnel_access_token: Optional[str] = Field(default=None, env="DEVTUNNEL_ACCESS_TOKEN")
    
    # Elasticsearch Configuration (for MCP server)
    elasticsearch_host: str = Field(default="localhost", env="ELASTICSEARCH_HOST")
    elasticsearch_port: int = Field(default=9200, env="ELASTICSEARCH_PORT")
    elasticsearch_username: Optional[str] = Field(default=None, env="ELASTICSEARCH_USERNAME")
    elasticsearch_password: Optional[str] = Field(default=None, env="ELASTICSEARCH_PASSWORD")
    elasticsearch_index: str = Field(default="default", env="ELASTICSEARCH_INDEX")
    
    # Azure Authentication (optional - DefaultAzureCredential is used by default)
    azure_client_id: Optional[str] = Field(default=None, env="AZURE_CLIENT_ID")
    azure_client_secret: Optional[str] = Field(default=None, env="AZURE_CLIENT_SECRET")
    azure_tenant_id: Optional[str] = Field(default=None, env="AZURE_TENANT_ID")
    
    # Agent Configuration
    agent_name: str = Field(default="elasticsearch-mcp-agent", env="AGENT_NAME")
    agent_instructions: str = Field(
        default="You are a helpful agent that can search and analyze data using Elasticsearch. "
                "You have access to an MCP (Model Context Protocol) server that provides "
                "Elasticsearch search capabilities. Use the search tools to help users find "
                "and analyze data effectively.",
        env="AGENT_INSTRUCTIONS"
    )
    
    @validator('project_endpoint')
    def validate_project_endpoint(cls, v):
        """Validate that the project endpoint is properly formatted."""
        if not v:
            raise ValueError("PROJECT_ENDPOINT must be set")
        if not v.startswith('https://'):
            raise ValueError("PROJECT_ENDPOINT must start with 'https://'")
        if 'services.ai.azure.com' not in v:
            raise ValueError("PROJECT_ENDPOINT must contain 'services.ai.azure.com'")
        return v
    
    @validator('model_deployment_name')
    def validate_model_deployment_name(cls, v):
        """Validate that the model deployment name is set."""
        if not v:
            raise ValueError("MODEL_DEPLOYMENT_NAME must be set")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_config() -> Config:
    """Get the application configuration."""
    try:
        return Config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("Please ensure you have copied .env.example to .env and filled in the required values.")
        raise


# Global configuration instance
config = get_config()
