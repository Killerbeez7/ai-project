import streamlit as st
import requests
import time

def chat_interface():
    """Render the chat interface for conversational PC building."""
    
    st.title("💬 Chat with the PC Build Expert")
    st.markdown("Have a conversation about your PC building needs. Ask questions, get recommendations, and refine your build!")
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! I'm your PC building expert. Tell me about what kind of computer you want to build - what's your budget and what will you use it for?"}
        ]
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about PC builds, components, or get recommendations..."):
        # Add user message to history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # This would call the LangChain agent endpoint
                    # For now, we'll simulate a response
                    response = get_agent_response(prompt)
                    st.write(response)
                    
                    # Add assistant response to history
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {e}"
                    st.write(error_msg)
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! I'm your PC building expert. Tell me about what kind of computer you want to build - what's your budget and what will you use it for?"}
        ]
        st.rerun()

def get_agent_response(user_message: str) -> str:
    """Get response from the recommendation system."""
    
    # Simple keyword extraction for budget and usage
    budget = extract_budget(user_message)
    usage = extract_usage(user_message)
    
    if budget and usage:
        # Call the actual API
        try:
            API_URL = "http://localhost:8000"  # or your deployed API
            response = requests.get(f"{API_URL}/v1/build", params={"budget": budget, "usage": usage})
            
            if response.status_code == 200:
                data = response.json()
                return format_build_response(data, user_message, budget, usage)
            else:
                return f"I found a ${budget} budget for {usage}, but couldn't generate a build. Try a higher budget?"
        except Exception as e:
            return f"I'd love to help with a ${budget} {usage} build, but I'm having technical difficulties. Please try the main form interface!"
    else:
        # Ask for clarification
        return ask_for_details(user_message)

def extract_budget(message: str) -> float:
    """Extract budget from user message."""
    import re
    # Look for patterns like $2300, 2300 dollars, etc.
    patterns = [
        r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $2300, $2,300
        r'(\d+(?:,\d{3})*(?:\.\d{2})?) dollars',  # 2300 dollars
        r'budget.{0,10}(\d+(?:,\d{3})*)',  # budget of 2300
        r'up to.{0,10}\$?(\d+(?:,\d{3})*)',  # up to $2300
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            budget_str = match.group(1).replace(',', '')
            try:
                return float(budget_str)
            except:
                continue
    return None

def extract_usage(message: str) -> str:
    """Extract usage type from user message."""
    message_lower = message.lower()
    
    # Gaming keywords
    if any(word in message_lower for word in ['game', 'gaming', 'gta', 'play', 'fps', 'esports']):
        return 'gaming'
    
    # Design keywords  
    if any(word in message_lower for word in ['design', 'photoshop', 'illustrator', 'creative', 'graphics']):
        return 'design'
    
    # Video editing keywords
    if any(word in message_lower for word in ['video', 'editing', 'premiere', 'render', 'streaming']):
        return 'video_editing'
        
    # Office keywords
    if any(word in message_lower for word in ['office', 'work', 'documents', 'excel', 'email']):
        return 'office_work'
    
    return 'gaming'  # Default assumption

def format_build_response(build_data: dict, original_message: str, budget: float, usage: str) -> str:
    """Format the API response into a conversational reply."""
    
    build = build_data.get('build', {})
    total_cost = build_data.get('total_cost', 0)
    
    if not build:
        return f"I couldn't generate a complete build for ${budget} and {usage} use. Try increasing your budget!"
    
    # Create a conversational response
    response = f"Great question! For a ${budget} {usage} build, I've got a perfect recommendation:\n\n"
    
    response += f"**Your Build (${total_cost:.2f}):**\n"
    for component_type, component in build.items():
        name = component.get('name', 'Unknown')
        price = component.get('price', 0)
        response += f"• **{component_type.replace('_', ' ').title()}**: {name} (${price:.2f})\n"
    
    # Add the AI explanation if available
    explanation = build_data.get('explanation', '')
    if explanation:
        response += f"\n**Why this build works for you:**\n{explanation}\n"
    
    # Add interactive suggestions
    response += f"\n💡 **Want to customize?** You can swap any component or adjust the budget. What would you like to change?"
    
    return response

def ask_for_details(message: str) -> str:
    """Ask user for missing budget or usage information."""
    
    has_budget = extract_budget(message) is not None
    has_usage = extract_usage(message) != 'gaming'  # Check if we detected specific usage
    
    if not has_budget and not has_usage:
        return "I'd love to help you build a PC! To give you the best recommendation, could you tell me:\n\n1. **What's your budget?** (e.g., $1000, $1500, $2000)\n2. **What will you use it for?** (gaming, design work, video editing, office tasks)\n\nFor example: 'I want a $1500 gaming PC' or 'I need a computer for photo editing with a $2000 budget'"
    
    elif not has_budget:
        return f"Sounds like you want a PC for {extract_usage(message)}! What's your budget for this build? (e.g., $1000, $1500, $2000)"
    
    elif not has_usage:
        budget = extract_budget(message)
        return f"Great! I see you have a ${budget} budget. What will you primarily use this PC for?\n\n• **Gaming** (playing games, streaming)\n• **Design** (Photoshop, graphic design)\n• **Video Editing** (Premiere, rendering)\n• **Office Work** (documents, web browsing)"
    
    return "I'm not sure I understood your request. Could you tell me your budget and what you'll use the PC for?"

if __name__ == "__main__":
    chat_interface() 