import streamlit as st
import requests
import time
import os

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
            with st.spinner("Analyzing your requirements..."):
                try:
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

def get_api_url():
    """Get the correct API URL for the current environment."""
    # Check if we're in development or production
    if os.getenv("STREAMLIT_ENV") == "development":
        return "http://localhost:8000"
    else:
        # Use the deployed API URL
        return "https://build-a-rig.onrender.com"

def get_agent_response(user_message: str) -> str:
    """Get response from the recommendation system."""
    
    # Simple keyword extraction for budget and usage
    budget = extract_budget(user_message)
    usage = extract_usage(user_message)
    
    if budget and usage:
        # Call the actual API
        try:
            api_url = get_api_url()
            
            # Add retry logic for cold starts
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        f"{api_url}/v1/build", 
                        params={"budget": budget, "usage": usage},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return format_build_response(data, user_message, budget, usage)
                    elif response.status_code == 502 and attempt < max_retries - 1:
                        # Cold start - wait and retry
                        time.sleep(5)
                        continue
                    else:
                        return f"I found a ${budget} budget for {usage}, but couldn't generate a build right now. Status: {response.status_code}. Please try again!"
                        
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue
                    else:
                        return f"The recommendation service is taking longer than expected. Please try again in a moment!"
                        
        except Exception as e:
            return f"I'd love to help with a ${budget} {usage} build, but I'm having technical difficulties: {str(e)}. Please try the main form interface!"
    else:
        # Ask for clarification
        return ask_for_details(user_message)

def extract_budget(message: str) -> float:
    """Extract budget from user message."""
    import re
    # Look for patterns like $2300, 2300 dollars, 1700$, etc.
    patterns = [
        r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $2300, $2,300
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\$',  # 1700$, 2300$
        r'(\d+(?:,\d{3})*(?:\.\d{2})?) dollars',  # 2300 dollars
        r'budget.{0,10}(\d+(?:,\d{3})*)',  # budget of 2300
        r'up to.{0,10}\$?(\d+(?:,\d{3})*)',  # up to $2300
        r'around.{0,10}\$?(\d+(?:,\d{3})*)',  # around $2300
        r'(\d{3,5})(?!\d)',  # standalone numbers 1000-99999
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            budget_str = match.group(1).replace(',', '')
            try:
                budget = float(budget_str)
                # Reasonable budget range check
                if 500 <= budget <= 10000:
                    return budget
            except:
                continue
    return None

def extract_usage(message: str) -> str:
    """Extract usage type from user message."""
    message_lower = message.lower()
    
    # Gaming keywords
    if any(word in message_lower for word in ['game', 'gaming', 'gta', 'play', 'fps', 'esports', 'steam', 'valorant', 'fortnite']):
        return 'gaming'
    
    # Design keywords  
    if any(word in message_lower for word in ['design', 'photoshop', 'illustrator', 'creative', 'graphics', 'art', 'drawing']):
        return 'design'
    
    # Video editing keywords
    if any(word in message_lower for word in ['video', 'editing', 'premiere', 'render', 'streaming', 'youtube', 'content']):
        return 'video_editing'
        
    # Office keywords
    if any(word in message_lower for word in ['office', 'work', 'documents', 'excel', 'email', 'productivity', 'business']):
        return 'office_work'
    
    return 'gaming'  # Default assumption

def format_build_response(build_data: dict, original_message: str, budget: float, usage: str) -> str:
    """Format the API response into a conversational reply."""
    
    build = build_data.get('build', {})
    total_cost = build_data.get('total_cost', 0)
    explanation = build_data.get('explanation', '')
    
    if not build:
        return f"I couldn't generate a complete build for ${budget} and {usage} use. Try increasing your budget to at least $600!"
    
    # Create a conversational response
    response = f"Perfect! I've designed a ${budget} {usage} build for you:\n\n"
    
    response += f"## 🖥️ Your Custom Build (${total_cost:.2f})\n\n"
    
    # Group components logically
    component_order = ['cpu', 'motherboard', 'memory', 'video_card', 'internal_hard_drive', 'power_supply', 'case']
    
    for component_type in component_order:
        if component_type in build:
            component = build[component_type]
            name = component.get('name', 'Unknown')
            price = component.get('price', 0)
            
            # Add emoji for each component type
            emoji_map = {
                'cpu': '🧠',
                'motherboard': '🔌', 
                'memory': '💾',
                'video_card': '🎮',
                'internal_hard_drive': '💿',
                'power_supply': '⚡',
                'case': '📦'
            }
            
            emoji = emoji_map.get(component_type, '🔧')
            display_name = component_type.replace('_', ' ').title()
            response += f"**{emoji} {display_name}**: {name} - ${price:.2f}\n"
    
    # Add any remaining components not in the order
    for component_type, component in build.items():
        if component_type not in component_order:
            name = component.get('name', 'Unknown')
            price = component.get('price', 0)
            display_name = component_type.replace('_', ' ').title()
            response += f"**🔧 {display_name}**: {name} - ${price:.2f}\n"
    
    # Add savings information
    savings = budget - total_cost
    if savings > 0:
        response += f"\n💰 **Great news!** This build comes in ${savings:.2f} under budget!\n"
    
    # Add the AI explanation if available
    if explanation:
        response += f"\n## 💡 Why This Build Works\n{explanation}\n"
    
    # Add interactive suggestions
    response += f"\n## 🎯 Next Steps\n"
    response += f"- Want to upgrade a component? Tell me which one!\n"
    response += f"- Need it cheaper? I can find alternatives\n"
    response += f"- Questions about compatibility? Just ask!\n"
    response += f"- Ready to buy? I can help you find the best prices\n"
    
    return response

def ask_for_details(message: str) -> str:
    """Ask user for missing budget or usage information."""
    
    detected_budget = extract_budget(message)
    detected_usage = extract_usage(message)
    
    # Check if we have meaningful detection (not just default)
    has_budget = detected_budget is not None
    has_specific_usage = any(word in message.lower() for word in [
        'gaming', 'design', 'video', 'editing', 'office', 'work', 'creative', 'streaming'
    ])
    
    if not has_budget and not has_specific_usage:
        return """I'd love to help you build the perfect PC! To give you the best recommendation, I need to know:

🎯 **What's your budget?** 
Examples: "$1500", "around $2000", "1700$ max"

🎮 **What will you use it for?**
• **Gaming** - Playing games, streaming, esports
• **Creative Work** - Photo editing, graphic design, art
• **Video Production** - Video editing, rendering, YouTube
• **Office Tasks** - Work, documents, web browsing

Just tell me something like: *"I want a $1500 gaming PC"* or *"I need a computer for video editing with a $2000 budget"*"""
    
    elif not has_budget:
        usage_display = detected_usage.replace('_', ' ')
        return f"""Great! I can see you want a PC for **{usage_display}**. 

💰 **What's your budget for this build?**

Some popular ranges:
• **$800-1200** - Great entry level
• **$1200-1800** - Excellent performance  
• **$1800-3000** - High-end/enthusiast
• **$3000+** - No compromises

Just tell me like: *"$1500"* or *"around $2000"* or *"1700$ max"*"""
    
    elif not has_specific_usage:
        return f"""Perfect! I see you have a **${detected_budget}** budget. 

🎯 **What will you primarily use this PC for?**

• 🎮 **Gaming** - Playing games, streaming, esports
• 🎨 **Creative Work** - Photoshop, graphic design, art  
• 🎬 **Video Production** - Video editing, rendering, content creation
• 💼 **Office/Productivity** - Work tasks, documents, web browsing

Just tell me the main use and I'll optimize the build for that!"""
    
    return """I want to make sure I understand your needs correctly. Could you tell me:

1. **Your budget** (e.g., $1500, $2000)
2. **Primary use** (gaming, creative work, video editing, office tasks)

This helps me recommend the perfect components for your specific needs!"""

if __name__ == "__main__":
    chat_interface() 