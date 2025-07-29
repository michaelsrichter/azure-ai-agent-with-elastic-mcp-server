#!/bin/bash

# Setup script for Azure AI Foundry Agent with MCP Server
echo "Setting up Azure AI Foundry Agent with MCP Server..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your actual values."
    echo ""
    echo "Required configuration:"
    echo "  - PROJECT_ENDPOINT: Your Azure AI Foundry project endpoint"
    echo "  - MODEL_DEPLOYMENT_NAME: Your model deployment name"
    echo "  - ELASTICSEARCH_* settings for your MCP server"
    echo ""
    echo "📖 See README.md for detailed setup instructions"
else
    echo "✅ .env file already exists"
fi

# Check Azure CLI
if command -v az &> /dev/null; then
    echo "✅ Azure CLI is installed"
    
    # Check if logged in
    az account show &> /dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Azure CLI is authenticated"
    else
        echo "⚠️  Azure CLI is not authenticated. Run 'az login' to authenticate."
    fi
else
    echo "⚠️  Azure CLI is not installed. Install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Azure AI Foundry and Elasticsearch settings"
echo "2. Ensure your MCP server is running at localhost:8080/mcp"
echo "3. Run 'python test_setup.py' to verify your configuration"
echo "4. Run 'python examples.py' to see the agent in action"
echo ""
echo "📖 For detailed instructions, see README.md"
