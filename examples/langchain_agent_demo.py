"""
Demo script for the LangChain PC Build Agent.
Shows how to use the tools and agent for conversational PC building assistance.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.recommend_tool import recommend_pc_build, get_component_options
from src.agents.pc_build_agent import PCBuildAgent, get_ai_build_recommendation

def demo_direct_tool_usage():
    """Demonstrate using the tools directly."""
    print("=== Direct Tool Usage Demo ===\n")
    
    # Test the recommendation tool
    print("1. Getting a gaming build for $1500:")
    result = recommend_pc_build.invoke({"budget": 1500, "usage": "gaming"})
    print(result[:200] + "...\n")
    
    # Test the component options tool
    print("2. Getting CPU options under $300:")
    result = get_component_options.invoke({"component_type": "cpu", "max_price": 300})
    print(result[:200] + "...\n")

def demo_conversational_agent():
    """Demonstrate using the conversational agent."""
    print("=== Conversational Agent Demo ===\n")
    
    # Create an agent
    agent = PCBuildAgent()
    
    # Simulate a conversation
    queries = [
        "I want to build a gaming PC but I'm not sure about the budget",
        "I have around $2000 to spend",
        "What if I want to do some video editing too?",
        "Can you explain why you chose that graphics card?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"User {i}: {query}")
        response = agent.chat(query)
        print(f"Agent: {response[:150]}...\n")

def demo_simple_function():
    """Demonstrate the simple function interface."""
    print("=== Simple Function Interface Demo ===\n")
    
    response = get_ai_build_recommendation(
        "I need a computer for graphic design work",
        budget=1800,
        usage="design"
    )
    print(f"Response: {response[:200]}...\n")

def interactive_demo():
    """Interactive demo where user can chat with the agent."""
    print("=== Interactive Demo ===")
    print("Chat with the PC Build Agent! Type 'quit' to exit.\n")
    
    agent = PCBuildAgent()
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Thanks for using the PC Build Agent!")
            break
        
        if user_input.lower() == 'reset':
            agent.reset_conversation()
            print("Conversation reset!\n")
            continue
        
        try:
            response = agent.chat(user_input)
            print(f"Agent: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    import os
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Some demos may not work without it.\n")
    
    print("LangChain PC Build Agent Demonstration")
    print("=" * 40)
    
    # Run demos
    try:
        demo_direct_tool_usage()
    except Exception as e:
        print(f"Direct tool demo failed: {e}\n")
    
    try:
        demo_simple_function()
    except Exception as e:
        print(f"Simple function demo failed: {e}\n")
    
    # Ask if user wants interactive demo
    if input("Run interactive demo? (y/n): ").lower().startswith('y'):
        interactive_demo() 