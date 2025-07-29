#!/usr/bin/env python3
"""Test Azure AI agent search functionality specifically."""

import asyncio
import sys
import os
from datetime import datetime

print(f"🔍 Azure AI Agent Search Test")
print(f"Started at: {datetime.now()}")
print("=" * 50)

try:
    print("1. Importing modules...")
    from azure_ai_agent import AzureAIMCPAgent
    from config import Config
    print(f"   ✅ Imports successful")
    
    config = Config()
    print(f"   📊 Elasticsearch index: {config.elasticsearch_index}")
    
    async def test_search():
        agent = None
        try:
            print("\n2. Creating and initializing agent...")
            agent = AzureAIMCPAgent()
            await agent.initialize()
            print("   ✅ Agent initialized")
            
            print("\n3. Creating Azure AI agent...")
            agent_id = await agent.create_agent()
            print(f"   ✅ Agent created with ID: {agent_id}")
            
            print("\n4. Creating conversation thread...")
            thread_id = await agent.create_thread()
            print(f"   ✅ Thread created with ID: {thread_id}")
            
            print("\n5. Testing search functionality...")
            search_message = (
                "Please search the nyc-art-galleries index using the search tool. "
                "Use a match_all query and return 3 results. "
                "Show me the names and contact information of the galleries."
            )
            
            await agent.send_message(search_message)
            print("   ✅ Search message sent")
            
            print("\n6. Running agent to execute search...")
            result = await agent.run_agent()
            print(f"   ✅ Agent run completed with status: {result.get('status', 'unknown')}")
            
            if result.get('messages'):
                print(f"   📨 Got {len(result['messages'])} messages")
                # Show the response from assistant
                for msg in result['messages']:
                    if msg.get('role') == 'assistant':
                        content_parts = msg.get('content', [])
                        if isinstance(content_parts, list):
                            for part in content_parts:
                                if part.get('type') == 'text':
                                    text_content = part.get('text', {})
                                    value = text_content.get('value', '') if isinstance(text_content, dict) else str(text_content)
                                    print(f"   🤖 Assistant: {value[:300]}{'...' if len(value) > 300 else ''}")
                        else:
                            print(f"   🤖 Assistant: {str(content_parts)[:300]}...")
            
            if result.get('status') == 'failed':
                print(f"   ❌ Run failed: {result.get('error', 'Unknown error')}")
                return False
            
        except Exception as e:
            print(f"   ❌ Error in search test: {e}")
            return False
            
        finally:
            if agent:
                try:
                    print("\n7. Cleaning up...")
                    await agent.cleanup()
                    print("   ✅ Cleanup completed")
                except Exception as e:
                    print(f"   ⚠️ Cleanup warning: {e}")
        
        return True
    
    print("\n🎯 Starting search test...")
    success = asyncio.run(test_search())
    
    if success:
        print("\n🎉 Search test completed successfully!")
    else:
        print("\n💥 Search test failed!")
        
except Exception as e:
    print(f"❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()

print(f"\nFinished at: {datetime.now()}")
