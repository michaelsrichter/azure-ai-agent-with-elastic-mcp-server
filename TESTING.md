# Manual Testing Guide for Azure AI Agent with MCP Server

## Prerequisites Checklist

Before testing, ensure you have:

- [ ] Azure AI Foundry project set up
- [ ] Model deployed (e.g., GPT-4o) in your Azure AI project
- [ ] Azure CLI installed and logged in (`az login`)
- [ ] Elasticsearch running (locally or remotely)
- [ ] MCP server running on http://localhost:8080/mcp
- [ ] All environment variables filled in `.env` file

## Testing Steps

### Step 1: Environment Setup

1. **Copy and configure environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

2. **Required .env values:**
   - `PROJECT_ENDPOINT`: Your Azure AI Foundry project endpoint
   - `MODEL_DEPLOYMENT_NAME`: Your deployed model name (e.g., "gpt-4o")
   - `MCP_SERVER_URL`: Usually "http://localhost:8080/mcp"
   - `ELASTICSEARCH_HOST`: Your Elasticsearch host
   - `ELASTICSEARCH_PORT`: Usually 9200
   - `ELASTICSEARCH_INDEX`: The index you want to search

### Step 2: Install Dependencies

```bash
# Recommended: use a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt
```

### Step 3: Test MCP Server Connection

```bash
# Test basic MCP connection
python3 test_setup.py
```

**Expected output:**
```
✓ Connected to MCP server at http://localhost:8080/mcp
✓ Found X available tools:
  - elasticsearch_search: Search documents in Elasticsearch
  - elasticsearch_mapping: Get index mapping
  - ...
```

### Step 4: Run Integration Tests

```bash
# Run comprehensive tests
./run_tests.sh
# OR
python3 test_integration.py
```

**Expected test sequence:**
1. ✅ Basic Setup and Configuration
2. ✅ MCP Server Connection
3. ✅ Elasticsearch Connection via MCP
4. ✅ Azure AI Agent Creation
5. ✅ Simple Conversation
6. ✅ Tool Usage with Elasticsearch Search

### Step 5: Manual Interactive Testing

```bash
# Run the main agent
python3 azure_ai_agent.py
```

**Try these sample queries:**
- "Hello, can you introduce yourself?"
- "What tools do you have available?"
- "Can you search for documents containing 'machine learning' in Elasticsearch?"
- "Show me the mapping of the current Elasticsearch index"
- "Search for the top 5 most recent documents"

## Troubleshooting Common Issues

### Issue: "Failed to authenticate with Azure"
**Solution:**
```bash
# Login to Azure CLI
az login

# Verify your subscription
az account show

# If needed, set the correct subscription
az account set --subscription "your-subscription-id"
```

### Issue: "Cannot connect to MCP server"
**Solutions:**
1. Make sure your MCP server is running:
   ```bash
   # Check if server is responding
   curl http://localhost:8080/mcp/health
   ```
2. Verify the URL in your `.env` file
3. Check firewall settings

### Issue: "Model deployment not found"
**Solutions:**
1. Verify your model deployment name in Azure AI Foundry
2. Make sure the model is fully deployed and not in "Creating" state
3. Check that `MODEL_DEPLOYMENT_NAME` in `.env` matches exactly

### Issue: "Elasticsearch connection failed"
**Solutions:**
1. Make sure Elasticsearch is running:
   ```bash
   curl http://localhost:9200
   ```
2. Check credentials if authentication is required
3. Verify the index exists:
   ```bash
   curl http://localhost:9200/_cat/indices
   ```

### Issue: "Agent created but no tool calls"
**Possible causes:**
1. MCP tools not properly registered
2. Tool schemas incompatible
3. Agent instructions not clear enough

**Debug steps:**
1. Check available tools: The test script will list them
2. Review agent instructions in `config.py`
3. Make queries more explicit about using tools

## Verification Checklist

After running tests, verify:

- [ ] Azure AI agent can be created successfully
- [ ] MCP server connection is established
- [ ] Tools are properly registered with the agent
- [ ] Agent can have basic conversations
- [ ] Agent can execute Elasticsearch searches via MCP
- [ ] Tool results are properly returned to the agent
- [ ] Agent can interpret and explain search results

## Performance Testing

For production readiness, also test:

1. **Load testing:** Multiple concurrent requests
2. **Error handling:** Invalid queries, network timeouts
3. **Large result sets:** Searches returning many documents
4. **Different query types:** Full-text, filters, aggregations

## Logs and Debugging

Key log files and debug information:
- Agent logs: Console output with timestamp
- MCP server logs: Check your MCP server implementation
- Azure AI logs: Available in Azure portal
- Elasticsearch logs: Check Elasticsearch server logs

Set log level for more detail:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
