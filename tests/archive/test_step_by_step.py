#!/usr/bin/env python3
"""Test Azure AI agent step by step."""

import asyncio
import sys
import os
from datetime import datetime

print(f"🚀 Azure AI Agent Step-by-Step Test")
print(f"Started at: {datetime.now()}")
print("=" * 50)

try:
    print("1. Importing modules...")
    from azure_ai_agent import AzureAIMCPAgent
    from config import Config
    print(f"   ✅ Imports successful")
    
    config = Config()
    print(f"   📊 Elasticsearch index: {config.elasticsearch_index}")
    
    async def test_step_by_step():
        agent = None
        try:
            print("\n2. Creating agent instance...")
            agent = AzureAIMCPAgent()
            print("   ✅ Agent instance created")
            
            print("\n3. Initializing agent (this may take a moment)...")
            await agent.initialize()
            print("   ✅ Agent initialized")
            
            print("\n4. Creating Azure AI agent...")
            agent_id = await agent.create_agent()
            print(f"   ✅ Agent created with ID: {agent_id}")
            
            print("\n5. Creating conversation thread...")
            thread_id = await agent.create_thread()
            print(f"   ✅ Thread created with ID: {thread_id}")
            
            print("\n6. Sending test message...")
            await agent.send_message("Hello! Please tell me what tools you have available.")
            print("   ✅ Message sent")
            
            print("\n7. Running agent...")
            result = await agent.run_agent()
            print(f"   ✅ Agent run completed with status: {result.get('status', 'unknown')}")
            
            if result.get('messages'):
                print(f"   📨 Got {len(result['messages'])} messages")
                # Show the last message from assistant
                for msg in result['messages']:
                    if msg.get('role') == 'assistant':
                        content = msg.get('content', '')
                        print(f"   🤖 Assistant: {content[:100]}{'...' if len(content) > 100 else ''}")
            
        except Exception as e:
            print(f"   ❌ Error in step: {e}")
            return False
            
        finally:
            if agent:
                try:
                    print("\n8. Cleaning up...")
                    await agent.cleanup()
                    print("   ✅ Cleanup completed")
                except Exception as e:
                    print(f"   ⚠️ Cleanup warning: {e}")
        
        return True
    
    print("\n🎯 Starting async test...")
    success = asyncio.run(test_step_by_step())
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
        
except Exception as e:
    print(f"❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()

print(f"\nFinished at: {datetime.now()}")
