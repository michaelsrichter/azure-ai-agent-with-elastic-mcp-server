# MCP Agent Python - Test Suite

This directory contains comprehensive tests for the Azure AI MCP Agent integrating with Elasticsearch through MCP Server.

## Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── run_tests.py                   # Main test runner
├── auth/                          # Authentication tests
│   └── test_devtunnel_auth.py    # DevTunnel authentication validation
├── integration/                   # End-to-end integration tests
│   ├── test_mcp_setup.py         # MCP server connection and setup
│   ├── test_agent_filtering.py   # Tool filtering and restrictions
│   └── test_nyc_galleries.py     # NYC Art Galleries search tests
└── unit/                          # Unit tests (future)
```

## Quick Start

### Run All Tests
```bash
# From the project root directory
python tests/run_tests.py
```

### Run Individual Test Categories

```bash
# Authentication tests
python tests/auth/test_devtunnel_auth.py

# MCP setup validation
python tests/integration/test_mcp_setup.py

# Tool filtering tests
python tests/integration/test_agent_filtering.py

# NYC galleries search tests
python tests/integration/test_nyc_galleries.py
```

## Environment Requirements

Before running tests, ensure these environment variables are set:

```bash
# Required
MCP_SERVER_URL=https://your-devtunnel-url.com/mcp
AZURE_OPENAI_API_KEY=your-azure-openai-key

# For DevTunnel authentication
DEVTUNNEL_ACCESS_TOKEN=your-devtunnel-token

# Elasticsearch configuration
ELASTICSEARCH_INDEX=nyc-art-galleries
```

## Test Categories

### 🔐 Authentication Tests (`auth/`)
- **DevTunnel Authentication**: Validates different authentication methods with the devtunnel MCP server
- Tests both unauthenticated and token-based authentication
- Verifies proper tunnel access token handling

### 🔗 Integration Tests (`integration/`)
- **MCP Setup**: Tests basic MCP server connection and tool availability
- **Agent Filtering**: Validates that the agent correctly filters out esql tool
- **NYC Galleries**: End-to-end tests of searching the NYC art galleries index

### 🧪 Unit Tests (`unit/`)
- Individual component tests (to be added)
- Mock-based testing for isolated functionality

## Test Results

Tests provide detailed output with:
- ✅ Success indicators for passing tests
- ❌ Failure indicators with error details
- 📊 Summary reports for each test suite
- 🎉 Overall pass/fail status

## Expected Test Flow

1. **Authentication Tests**: Verify devtunnel access is working
2. **MCP Setup Tests**: Confirm MCP server connectivity and tool availability
3. **Agent Filtering Tests**: Validate tool restrictions (esql excluded)
4. **Search Functionality Tests**: Test actual search operations

## Troubleshooting

### Common Issues

1. **Authentication Failures**: 
   - Check `DEVTUNNEL_ACCESS_TOKEN` environment variable
   - Verify devtunnel is active and accessible

2. **MCP Connection Issues**:
   - Confirm `MCP_SERVER_URL` is correct
   - Check devtunnel status

3. **Search Timeouts**:
   - Normal for some operations through devtunnel
   - Tests are designed to handle and work around timeouts

4. **Missing Tools**:
   - Ensure MCP server is running with Elasticsearch tools
   - Check MCP server logs for errors

### Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env

# Load environment
source .env  # or use your preferred method
```

## Adding New Tests

### Authentication Tests
Add new files to `tests/auth/` following the pattern:
```python
#!/usr/bin/env python3
"""Test description."""

async def test_your_functionality():
    # Your test logic
    return success_boolean

if __name__ == "__main__":
    result = asyncio.run(test_your_functionality())
    exit(0 if result else 1)
```

### Integration Tests
Add new files to `tests/integration/` with similar structure plus:
```python
# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
```

The test runner will automatically discover and run new tests following the naming convention `test_*.py`.
