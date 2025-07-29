#!/usr/bin/env python3
"""
Test NYC Art Galleries conversational search functionality.

This test demonstrates a realistic conversational scenario where:
1. User searches for art galleries (general search)
2. After getting results, user asks for galleries with specific characteristics
3. The thread maintains memory between requests to provide contextual responses
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from azure_ai_agent import AzureAIMCPAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_tool_outputs(agent, step_name):
    """Helper function to print tool outputs from the agent."""
    print(f"\n🔍 MCP Tool Outputs - {step_name}:")
    print("-" * 50)
    
    if hasattr(agent, 'last_tool_outputs') and agent.last_tool_outputs:
        for i, output in enumerate(agent.last_tool_outputs, 1):
            print(f"Tool Call {i}:")
            print(f"  Tool: {output.get('tool_name', 'Unknown')}")
            print(f"  Arguments: {output.get('arguments', 'No arguments')}")
            print(f"  Raw Output: {output.get('output', 'No output')}")
            print()
    else:
        print("No tool outputs captured from agent run")
    
    print("-" * 50)


def print_agent_response(messages, step_name):
    """Helper function to print the agent's response."""
    if messages:
        # Get the last assistant message
        assistant_messages = [msg for msg in messages if msg.get('role') == 'assistant']
        if assistant_messages:
            last_msg = assistant_messages[0]  # Messages are in reverse order
            content = last_msg.get('content', [])
            if content and isinstance(content, list) and len(content) > 0:
                response = content[0].get('text', {}).get('value', 'No response')
                print(f"\n🤖 Agent Response - {step_name}:")
                print("-" * 50)
                print(response)
                print("-" * 50)
                return response
    
    print(f"\n❌ No agent response found for {step_name}")
    return None


async def test_conversational_gallery_search():
    """Test a realistic conversational search scenario for NYC art galleries."""
    
    print("🎨 Testing Conversational NYC Art Gallery Search")
    print("=" * 50)
    
    try:
        async with AzureAIMCPAgent() as agent:
            # Create agent and thread - SINGLE THREAD for conversation continuity
            await agent.create_agent()
            await agent.create_thread()
            
            print(f"✅ Agent ready with {len(agent.mcp_tools)} tools")
            print(f"📞 Thread ID: {agent.thread_id}")
            
            # STEP 1: Search for art galleries (general search to get familiar with data)
            print(f"\n📍 STEP 1: Searching for NYC art galleries...")
            
            first_query = """
            Please search the "nyc-art-galleries" index to show me some art galleries in NYC.
            
            Use the search tool with this query_body parameter:
            {
                "query": {"match_all": {}},
                "size": 8
            }
            
            Please list the galleries you find. Pay special attention to any that might specialize in Indian, Asian, or international art, and note any galleries that mention sculptures or 3D artwork.
            """
            
            await agent.send_message(first_query)
            await agent.run_agent()
            
            # Capture and display first search results
            print_tool_outputs(agent, "Initial Gallery Search")
            first_response = print_agent_response(await agent.get_messages(), "Initial Gallery Search")
            
            if not first_response:
                print("❌ Failed to get response for initial gallery search")
                return False
            
            # STEP 2: Follow-up question about sculptures (using thread memory)
            print(f"\n🗿 STEP 2: Following up about sculptures in the same thread...")
            
            second_query = """
            Based on the galleries you just showed me, I'm particularly interested in galleries that feature sculptures or 3D artwork. 
            
            From your previous search results, can you tell me which galleries might have sculptural works? Also, please do another search to find more galleries that specifically mention sculptures:
            
            {
                "query": {"match_all": {}},
                "size": 10
            }
            
            Look through these results for any mention of sculptures, sculptural works, 3D art, or installations. Compare these with the galleries from your first search and recommend the best options for someone interested in sculptural art.
            """
            
            await agent.send_message(second_query)
            await agent.run_agent()
            
            # Capture and display second search results
            print_tool_outputs(agent, "Sculpture Follow-up Search")
            second_response = print_agent_response(await agent.get_messages(), "Sculpture Follow-up Search")
            
            if not second_response:
                print("❌ Failed to get response for sculpture follow-up")
                return False
            
            # STEP 3: Final follow-up to test deeper memory
            print(f"\n🎯 STEP 3: Testing deeper thread memory...")
            
            third_query = """
            Perfect! Now from all the galleries we've discussed - both from your first general search and your sculpture-focused search - can you give me your top 3 recommendations for someone who wants to see both international art (especially Indian/Asian) AND sculptures? 
            
            Please don't do another search, just use the information from our previous conversations in this thread to make your recommendations.
            """
            
            await agent.send_message(third_query)
            await agent.run_agent()
            
            # Capture final response
            third_response = print_agent_response(await agent.get_messages(), "Final Recommendations")
            
            # STEP 4: Validate thread memory by getting full conversation
            print(f"\n💭 STEP 4: Validating thread memory - Full conversation:")
            print("-" * 50)
            
            all_messages = await agent.get_messages()
            conversation_pairs = []
            
            # Group messages into user/assistant pairs
            for i, message in enumerate(reversed(all_messages)):  # Reverse to get chronological order
                role = message.get('role', 'unknown')
                content = message.get('content', [])
                if content and isinstance(content, list) and len(content) > 0:
                    text = content[0].get('text', {}).get('value', 'No content')
                    conversation_pairs.append((role, text[:150] + "..." if len(text) > 150 else text))
            
            # Display conversation flow
            for i, (role, content) in enumerate(conversation_pairs):
                print(f"{role.upper()}: {content}")
                if i < len(conversation_pairs) - 1:
                    print()
            
            print("-" * 50)
            
            # Validate conversational context
            thread_memory_working = False
            if second_response:
                # Check if the second response references the first search
                memory_indicators = [
                    "from the", "you just", "previously", "earlier", "first search", 
                    "your search", "the galleries", "from your", "based on"
                ]
                
                for indicator in memory_indicators:
                    if indicator in second_response.lower():
                        thread_memory_working = True
                        print(f"✅ Thread memory detected: Found reference '{indicator}'")
                        break
            
            # Check if third response references previous conversations
            deeper_memory_working = False
            if third_response:
                deeper_indicators = [
                    "from all the galleries", "we've discussed", "both from your", "previous conversations",
                    "our conversation", "all the galleries", "from our", "we talked about"
                ]
                
                for indicator in deeper_indicators:
                    if indicator in third_response.lower():
                        deeper_memory_working = True
                        print(f"✅ Deeper thread memory detected: Found reference '{indicator}'")
                        break
            
            if not thread_memory_working:
                print("⚠️  Basic thread memory may not be working")
            if not deeper_memory_working:
                print("⚠️  Deeper thread memory may not be working")
            
            # Final assessment
            success_criteria = [
                ("Initial gallery search completed", "gallery" in first_response.lower() if first_response else False),
                ("Sculpture follow-up completed", "sculpture" in second_response.lower() if second_response else False),
                ("Final recommendations provided", third_response is not None and len(third_response) > 50),
                ("Basic thread memory maintained", thread_memory_working),
                ("Deeper thread memory maintained", deeper_memory_working),
                ("Multiple tool calls executed", len(agent.last_tool_outputs) > 0 if hasattr(agent, 'last_tool_outputs') else False)
            ]
            
            print(f"\n📊 Success Criteria Assessment:")
            print("-" * 50)
            
            passed_count = 0
            for criterion, passed in success_criteria:
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"{criterion}: {status}")
                if passed:
                    passed_count += 1
            
            success_rate = passed_count / len(success_criteria)
            overall_success = success_rate >= 0.66  # At least 2/3 criteria must pass
            
            print(f"\nConversational Test Result: {'✅ SUCCESS' if overall_success else '⚠️  PARTIAL SUCCESS'} ({passed_count}/{len(success_criteria)} criteria passed)")
            return overall_success
                
    except Exception as e:
        print(f"❌ Conversational gallery search failed: {e}")
        logger.exception("Conversational search test failed")
        return False


async def run_test():
    """Run the conversational NYC galleries search test."""
    print("🧪 NYC Art Galleries Conversational Test")
    print("=" * 50)
    
    try:
        result = await test_conversational_gallery_search()
        
        print("\n📊 Test Results Summary")
        print("=" * 50)
        
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"Conversational Gallery Search: {status}")
        
        print(f"\nOverall: {'✅ TEST PASSED' if result else '❌ TEST FAILED'}")
        return result
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        logger.exception("Test execution failed")
        return False


if __name__ == "__main__":
    result = asyncio.run(run_test())
    exit(0 if result else 1)
