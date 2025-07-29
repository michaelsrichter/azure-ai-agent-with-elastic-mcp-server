#!/usr/bin/env python3
"""
Test runner for MCP Agent Python tests.

This script runs all tests in the proper order and provides
a comprehensive test report.
"""

import asyncio
import sys
import os
import importlib.util
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests


def load_test_module(test_path):
    """Load a test module from file path."""
    spec = importlib.util.spec_from_file_location("test_module", test_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def run_test_file(test_path):
    """Run a single test file."""
    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_path.name}")
        print(f"{'='*60}")
        
        module = load_test_module(test_path)
        
        # Look for main test function
        if hasattr(module, 'run_all_tests'):
            result = await module.run_all_tests()
        elif hasattr(module, 'main'):
            result = await module.main()
        else:
            # Try to run the file directly
            original_argv = sys.argv
            sys.argv = [str(test_path)]
            try:
                # Execute the module's main section
                exec(open(test_path).read())
                result = True
            except SystemExit as e:
                result = e.code == 0
            finally:
                sys.argv = original_argv
        
        return result
        
    except Exception as e:
        print(f"❌ Failed to run {test_path.name}: {e}")
        return False


async def run_auth_tests():
    """Run authentication tests."""
    print("\n🔐 AUTHENTICATION TESTS")
    print("=" * 80)
    
    auth_dir = Path(__file__).parent / "auth"
    test_files = list(auth_dir.glob("test_*.py"))
    
    if not test_files:
        print("No authentication tests found")
        return True
    
    results = []
    for test_file in sorted(test_files):
        result = await run_test_file(test_file)
        results.append((test_file.name, result))
    
    return all(result for _, result in results)


async def run_integration_tests():
    """Run integration tests."""
    print("\n🔗 INTEGRATION TESTS")
    print("=" * 80)
    
    integration_dir = Path(__file__).parent / "integration"
    test_files = list(integration_dir.glob("test_*.py"))
    
    if not test_files:
        print("No integration tests found")
        return True
    
    # Run setup test first
    setup_tests = [f for f in test_files if 'setup' in f.name]
    other_tests = [f for f in test_files if 'setup' not in f.name]
    
    results = []
    
    # Run setup first
    for test_file in sorted(setup_tests):
        result = await run_test_file(test_file)
        results.append((test_file.name, result))
    
    # Run other tests
    for test_file in sorted(other_tests):
        result = await run_test_file(test_file)
        results.append((test_file.name, result))
    
    return all(result for _, result in results)


async def run_unit_tests():
    """Run unit tests."""
    print("\n🧪 UNIT TESTS")
    print("=" * 80)
    
    unit_dir = Path(__file__).parent / "unit"
    test_files = list(unit_dir.glob("test_*.py"))
    
    if not test_files:
        print("No unit tests found")
        return True
    
    results = []
    for test_file in sorted(test_files):
        result = await run_test_file(test_file)
        results.append((test_file.name, result))
    
    return all(result for _, result in results)


async def main():
    """Run all tests."""
    print("🚀 MCP Agent Python - Test Suite Runner")
    print("=" * 80)
    
    # Check environment
    required_env_vars = ["MCP_SERVER_URL", "AZURE_OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set these variables before running tests.")
        return False
    
    print("✅ Environment variables check passed")
    
    # Run test suites
    test_suites = [
        ("Authentication", run_auth_tests),
        ("Integration", run_integration_tests),
        ("Unit", run_unit_tests)
    ]
    
    suite_results = []
    
    for suite_name, suite_func in test_suites:
        try:
            result = await suite_func()
            suite_results.append((suite_name, result))
        except Exception as e:
            print(f"❌ {suite_name} test suite failed: {e}")
            suite_results.append((suite_name, False))
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for suite_name, passed in suite_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{suite_name} Tests: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Your MCP Agent is ready to go!")
    else:
        print("❌ SOME TESTS FAILED. Please check the output above.")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
