# Azure AI Foundry Agent with MCP Server Integration

This project demonstrates how to create an Azure AI Foundry agent in Python that connects to an MCP (Model Context Protocol) server for Elasticsearch integration. The agent can search, analyze, and interact with Elasticsearch data through natural language conversations.

## Features

- **Azure AI Foundry Integration**: Uses the latest Azure AI Projects SDK for agent creation and management
- **MCP Server Communication**: Connects to an MCP server for Elasticsearch integration
- **Tool Filtering**: Supports filtering MCP tools (e.g., exclude esql capability)
- **DevTunnel Support**: Works with Azure DevTunnels for secure remote access
- **Elasticsearch Tools**: Provides search, mapping, and analysis capabilities for Elasticsearch
- **Secure Configuration**: All credentials and URLs stored in environment variables
- **Comprehensive Error Handling**: Robust error handling and logging throughout
- **Async/Await Support**: Fully asynchronous implementation for better performance
- **Comprehensive Testing**: Organized test suite with authentication, integration, and functional tests

## Prerequisites

### Azure Requirements
- Azure AI Foundry project set up
- Azure AI User RBAC role assigned (at project scope)
- Model deployment (e.g., GPT-4o) in your Azure AI Foundry project

### Local Requirements
- Python 3.8 or higher
- MCP server running at localhost:8080/mcp
- Elasticsearch instance (accessible from MCP server)

## Installation

1. **Clone and navigate to the project:**
   ```bash
   git clone <your-repo>
   cd mcp-agent-python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your actual values:
   ```bash
   # Azure AI Foundry Configuration
   PROJECT_ENDPOINT=https://<AIFoundryResourceName>.services.ai.azure.com/api/projects/<ProjectName>
   MODEL_DEPLOYMENT_NAME=gpt-4o
   
   # MCP Server Configuration
   MCP_SERVER_URL=http://localhost:8080/mcp
   
   # Elasticsearch Configuration
   ELASTICSEARCH_HOST=localhost
   ELASTICSEARCH_PORT=9200
   ELASTICSEARCH_USERNAME=elastic
   ELASTICSEARCH_PASSWORD=your_password_here
   ELASTICSEARCH_INDEX=your_index_name
   ```

4. **Authenticate with Azure:**
   ```bash
   az login
   ```

## Getting Your Azure AI Foundry Configuration

### Project Endpoint
1. Go to [Azure AI Foundry portal](https://ai.azure.com/)
2. Navigate to your project
3. Go to Libraries > Azure AI Foundry
4. Copy the endpoint URL (format: `https://<resource>.services.ai.azure.com/api/projects/<project>`)

### Model Deployment Name
1. In your Azure AI Foundry project
2. Go to Models + Endpoints in the left navigation
3. Copy the deployment name of your model

## Usage

### Basic Example

```python
import asyncio
from azure_ai_agent import AzureAIMCPAgent

async def main():
    async with AzureAIMCPAgent() as agent:
        # Create agent and thread
        await agent.create_agent()
        await agent.create_thread()
        
        # Send a message
        await agent.send_message(
            "Search for documents containing 'machine learning' in Elasticsearch"
        )
        
        # Get response
        result = await agent.run_agent()
        
        # Display conversation
        for message in reversed(result['messages']):
            print(f"{message['role']}: {message['content']}")

asyncio.run(main())
```

### Run Examples

The project includes several examples demonstrating different use cases:

```bash
python examples.py
```

This will run:
- Basic Elasticsearch search
- Filtered search with specific criteria  
- Direct MCP server communication
- Multi-turn conversation with the agent

## Project Structure

```
mcp-agent-python/
├── azure_ai_agent.py      # Main Azure AI agent implementation
├── config.py              # Configuration management with validation
├── mcp_client.py          # MCP server communication client
├── elasticsearch_tools.py # Custom tools for Elasticsearch integration
├── examples.py            # Usage examples
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your actual environment variables (do not commit)
└── README.md             # This file
```

## Key Components

### AzureAIMCPAgent
The main agent class that orchestrates:
- Azure AI Foundry client initialization
- MCP server connection
- Tool integration
- Conversation management

### MCPClient
Handles communication with the MCP server:
- Tool discovery
- Tool execution
- Error handling
- Connection management

### ElasticsearchMCPTool
Provides Elasticsearch-specific tools:
- `elasticsearch_search`: Search documents
- `elasticsearch_mapping`: Get index structure
- `elasticsearch_analyze`: Analyze text with ES analyzers

## Configuration Options

The agent supports extensive configuration through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_ENDPOINT` | Azure AI Foundry project endpoint | Required |
| `MODEL_DEPLOYMENT_NAME` | Name of your model deployment | Required |
| `MCP_SERVER_URL` | MCP server URL | `http://localhost:8080/mcp` |
| `ELASTICSEARCH_HOST` | Elasticsearch host | `localhost` |
| `ELASTICSEARCH_PORT` | Elasticsearch port | `9200` |
| `ELASTICSEARCH_USERNAME` | ES username | None |
| `ELASTICSEARCH_PASSWORD` | ES password | None |
| `ELASTICSEARCH_INDEX` | Default index to search | `default` |
| `AGENT_NAME` | Agent name | `elasticsearch-mcp-agent` |
| `AGENT_INSTRUCTIONS` | Agent system prompt | See config.py |

## Error Handling

The agent includes comprehensive error handling:

- **Azure Authentication**: Handles credential and permission issues
- **MCP Server Connection**: Graceful fallback when MCP server is unavailable
- **Elasticsearch Errors**: Proper error reporting from search operations
- **Configuration Validation**: Validates all required settings on startup

## Security Best Practices

Following Azure development best practices:

- **No Hardcoded Credentials**: All sensitive data in environment variables
- **DefaultAzureCredential**: Uses Azure's recommended authentication pattern
- **Input Validation**: Validates configuration and user inputs
- **Secure Communication**: HTTPS for Azure connections
- **Minimal Permissions**: Agent uses least-privilege access patterns

## Testing

This project includes a comprehensive test suite to validate all functionality:

### Quick Testing

```bash
# Run all tests
./run_tests.sh

# Check environment setup
./run_tests.sh check

# Run specific test categories
./run_tests.sh auth         # Authentication tests
./run_tests.sh setup        # MCP server connection tests  
./run_tests.sh filtering    # Tool filtering tests
./run_tests.sh integration  # All integration tests
```

### Test Structure

```
tests/
├── run_tests.py                    # Main test runner
├── auth/                          # Authentication tests
│   └── test_devtunnel_auth.py     # DevTunnel authentication validation
├── integration/                   # End-to-end integration tests
│   ├── test_mcp_setup.py         # MCP server connection
│   ├── test_agent_filtering.py   # Tool filtering validation
│   └── test_nyc_galleries.py     # NYC galleries search tests
└── archive/                       # Old test files (reference only)
```

### Test Categories

- **Authentication Tests**: Validate DevTunnel and Azure authentication
- **Integration Tests**: End-to-end testing of agent functionality
- **Tool Filtering Tests**: Verify esql exclusion and tool restrictions
- **Search Tests**: Test actual Elasticsearch operations

See [tests/README.md](tests/README.md) for detailed testing documentation.

## Troubleshooting

### Common Issues

1. **"PROJECT_ENDPOINT must be set" error**
   - Ensure your `.env` file has the correct Azure AI Foundry project endpoint
   - Verify the endpoint format matches: `https://<resource>.services.ai.azure.com/api/projects/<project>`

2. **Authentication errors**
   - Run `az login` to authenticate with Azure
   - Ensure you have the Azure AI User role on your project

3. **MCP server connection failed**
   - Verify your MCP server is running at localhost:8080/mcp
   - Check MCP server logs for any issues
   - The agent will still work but without MCP tools

4. **Model deployment not found**
   - Verify your `MODEL_DEPLOYMENT_NAME` matches the deployment in Azure AI Foundry
   - Check that the model is deployed and running

### Debugging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about:
- Azure AI client operations
- MCP server communications
- Tool executions
- Error details

## Contributing

1. Follow Azure development best practices
2. Add comprehensive error handling
3. Include logging for debugging
4. Update documentation for new features
5. Test with various Elasticsearch configurations

## License

This project is provided as an example for educational purposes.

## References

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure AI Projects Python SDK](https://aka.ms/azsdk/azure-ai-projects/python/reference)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Azure Authentication with DefaultAzureCredential](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential)
