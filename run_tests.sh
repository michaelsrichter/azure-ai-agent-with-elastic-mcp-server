#!/bin/bash

# MCP Agent Python - Test Runner Script
# This script provides convenient ways to run tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 MCP Agent Python - Test Runner${NC}"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "azure_ai_agent.py" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Load environment from .env file if it exists
if [ -f .env ]; then
    echo -e "${BLUE}📄 Loading environment from .env file${NC}"
    set -a
    source .env
    set +a
fi

# Check environment variables
check_env() {
    local missing=()
    
    if [ -z "$MCP_SERVER_URL" ]; then
        missing+=("MCP_SERVER_URL")
    fi
    
    if [ -z "$PROJECT_ENDPOINT" ]; then
        missing+=("PROJECT_ENDPOINT")
    fi
    
    if [ -z "$MODEL_DEPLOYMENT_NAME" ]; then
        missing+=("MODEL_DEPLOYMENT_NAME")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Missing environment variables: ${missing[*]}${NC}"
        echo -e "${YELLOW}   Please set these in your .env file or environment${NC}"
        return 1
    fi
    
    # Check if Azure CLI is logged in
    if ! az account show &>/dev/null; then
        echo -e "${YELLOW}⚠️  Azure CLI not logged in${NC}"
        echo -e "${YELLOW}   Please run 'az login' to authenticate with Azure${NC}"
        return 1
    fi
    
    return 0
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  all          Run all tests (default)"
    echo "  auth         Run authentication tests only"
    echo "  integration  Run integration tests only"
    echo "  setup        Run setup/connection tests only"
    echo "  filtering    Run tool filtering tests only"
    echo "  check        Check environment and exit"
    echo "  help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Run all tests"
    echo "  $0 auth         # Run only authentication tests"
    echo "  $0 setup        # Check MCP server connection"
    echo "  $0 check        # Verify environment setup"
}

# Run specific test category
run_tests() {
    local category="$1"
    
    case "$category" in
        "auth")
            echo -e "${BLUE}🔐 Running Authentication Tests${NC}"
            python3 tests/auth/test_devtunnel_auth.py
            ;;
        "setup")
            echo -e "${BLUE}🔗 Running Setup/Connection Tests${NC}"
            python3 tests/integration/test_mcp_setup.py
            ;;
        "filtering")
            echo -e "${BLUE}🔧 Running Tool Filtering Tests${NC}"
            python3 tests/integration/test_agent_filtering.py
            ;;
        "nyc")
            echo -e "${BLUE}🎨 Running NYC Galleries Tests${NC}"
            python3 tests/integration/test_nyc_galleries.py
            ;;
        "integration")
            echo -e "${BLUE}🔗 Running All Integration Tests${NC}"
            python3 tests/integration/test_mcp_setup.py
            echo ""
            python3 tests/integration/test_agent_filtering.py
            echo ""
            python3 tests/integration/test_nyc_galleries.py
            ;;
        "all")
            echo -e "${BLUE}🧪 Running All Tests${NC}"
            python3 tests/run_tests.py
            ;;
        *)
            echo -e "${RED}❌ Unknown test category: $category${NC}"
            show_usage
            exit 1
            ;;
    esac
}

# Main script logic
case "${1:-all}" in
    "help"|"-h"|"--help")
        show_usage
        exit 0
        ;;
    "check")
        echo -e "${BLUE}🔍 Checking Environment${NC}"
        if check_env; then
            echo -e "${GREEN}✅ Environment check passed${NC}"
            echo -e "${GREEN}   MCP_SERVER_URL: ${MCP_SERVER_URL}${NC}"
            echo -e "${GREEN}   PROJECT_ENDPOINT: ${PROJECT_ENDPOINT}${NC}"
            echo -e "${GREEN}   MODEL_DEPLOYMENT_NAME: ${MODEL_DEPLOYMENT_NAME}${NC}"
            if [ -n "$DEVTUNNEL_ACCESS_TOKEN" ]; then
                echo -e "${GREEN}   DEVTUNNEL_ACCESS_TOKEN: [SET]${NC}"
            else
                echo -e "${YELLOW}   DEVTUNNEL_ACCESS_TOKEN: [NOT SET - may be needed for devtunnel auth]${NC}"
            fi
            echo -e "${GREEN}   Azure CLI: [LOGGED IN]${NC}"
            exit 0
        else
            exit 1
        fi
        ;;
    *)
        if ! check_env; then
            echo -e "${RED}❌ Environment check failed${NC}"
            echo "Run '$0 check' for details"
            exit 1
        fi
        
        echo -e "${GREEN}✅ Environment check passed${NC}"
        echo ""
        
        run_tests "$1"
        ;;
esac
