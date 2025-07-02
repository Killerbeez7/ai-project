import streamlit as st
import requests
import os
import time
import re

# Page config
st.set_page_config(
    page_title="Build a RIG - AI-guided PC configurator",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for stylish tabs and persistent context
st.markdown("""
<style>
/* Custom tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 5px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    padding: 10px 20px;
    background-color: transparent;
    border-radius: 8px;
    color: #666;
    font-weight: 500;
    border: none;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background-color: white;
    color: #1f77b4;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Context panel styling */
.context-panel {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.build-summary {
    background: #f8f9fa;
    border-left: 4px solid #1f77b4;
    padding: 15px;
    border-radius: 0 8px 8px 0;
    margin: 10px 0;
}

.quick-stats {
    display: flex;
    gap: 20px;
    align-items: center;
}
</style>
""", unsafe_allow_html=True)

# App state initialization
def init_session_state():
    """Initializes session state variables if they don't exist."""
    state_defaults = {
        'current_build': {},
        'candidates': {},
        'explanation': "",
        'total_cost': 0.0,
        'current_budget': 1500,
        'current_usage': "gaming",
        'last_build_generated': False,
        'chat_messages': [
            {"role": "assistant", "content": "👋 Hi! I'm your PC building expert. Tell me about what kind of computer you want to build - what's your budget and what will you use it for?"}
        ],
    }
    for key, value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Helper functions
def update_build_and_cost():
    """Recalculates the total cost of the build currently in the session state."""
    build = st.session_state.current_build
    if build:
        st.session_state.total_cost = sum(part.get('price', 0) for part in build.values())

def handle_part_change(part_type):
    """
    Updates the selected part in the current build and recalculates the cost.
    This function is called when a user changes a selection in a selectbox.
    """
    selected_name = st.session_state[f"{part_type}_selector"]
    part_options = st.session_state.candidates.get(part_type, [])
    
    new_part = next((p for p in part_options if p['name'] == selected_name), None)
    
    if new_part:
        st.session_state.current_build[part_type] = new_part
        update_build_and_cost()

def call_api_with_retry(budget, usage):
    """
    Calls the API with retry logic to handle cold starts gracefully.
    Tries immediately, then retries after 5 seconds if we get a 502 error.
    """
    params = {"budget": budget, "usage": usage}
    
    # API Configuration
    try:
        API_URL = st.secrets["API_URL"]
    except (KeyError, FileNotFoundError):
        API_URL = os.environ.get("API_URL", "http://localhost:8000")
    
    api_url = f"{API_URL}/v1/build"
    
    status_container = st.empty()
    
    for attempt, delay in enumerate([(0, "🔍 Analyzing parts, running combinations, and asking the AI for advice..."), 
                                     (5, "⏳ API is warming up (cold start), please wait...")], 1):
        sleep_time, message = delay
        
        if sleep_time > 0:
            status_container.info("🔄 Server is starting up (cold start). Retrying in 5 seconds...")
            time.sleep(sleep_time)
        
        try:
            with status_container:
                with st.spinner(message):
                    response = requests.get(api_url, params=params, timeout=30)
                    response.raise_for_status()
                    status_container.empty()
                    return response.json()  # SUCCESS!
                
        except requests.HTTPError as http_err:
            if response.status_code == 502 and attempt == 1:
                continue
            
            status_container.empty()
            try:
                error_detail = http_err.response.json().get("detail", "An unknown error occurred.")
            except:
                error_detail = http_err.response.text
            raise Exception(f"API Error ({response.status_code}): {error_detail}")
            
        except requests.RequestException as e:
            if attempt == 1:
                status_container.info("🔄 Connection issue. Retrying in 5 seconds...")
                continue  # Try again with delay
            status_container.empty()
            raise Exception(f"Failed to connect to the recommendation API: {e}")
    
    status_container.empty()
    raise Exception("API request failed after retries")

# Real Chat functionality (from pages/chat.py)
def get_api_url():
    """Get the correct API URL for the current environment."""
    if os.getenv("STREAMLIT_ENV") == "development":
        return "http://localhost:8000"
    else:
        return "https://build-a-rig.onrender.com"

def extract_budget(message: str) -> float:
    """Extract budget from user message."""
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
                if 500 <= budget <= 10000:
                    return budget
            except:
                continue
    return None

def extract_usage(message: str) -> str:
    """Extract usage type from user message."""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['game', 'gaming', 'gta', 'play', 'fps', 'esports', 'steam', 'valorant', 'fortnite']):
        return 'gaming'
    
    if any(word in message_lower for word in ['design', 'photoshop', 'illustrator', 'creative', 'graphics', 'art', 'drawing']):
        return 'design'
    
    if any(word in message_lower for word in ['video', 'editing', 'premiere', 'render', 'streaming', 'youtube', 'content']):
        return 'video_editing'
        
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
    
    response = f"Perfect! I've designed a ${budget} {usage} build for you:\n\n"
    response += f"## 🖥️ Your Custom Build (${total_cost:.2f})\n\n"
    
    component_order = ['cpu', 'motherboard', 'memory', 'video_card', 'internal_hard_drive', 'power_supply', 'case']
    
    for component_type in component_order:
        if component_type in build:
            component = build[component_type]
            name = component.get('name', 'Unknown')
            price = component.get('price', 0)
            
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
    
    savings = budget - total_cost
    if savings > 0:
        response += f"\n💰 **Great news!** This build comes in ${savings:.2f} under budget!\n"
    
    if explanation:
        response += f"\n## 💡 Why This Build Works\n{explanation}\n"
    
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

def get_agent_response(user_message: str) -> str:
    """Get response from the recommendation system."""
    
    budget = extract_budget(user_message)
    usage = extract_usage(user_message)
    
    if budget and usage:
        try:
            api_url = get_api_url()
            
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
        return ask_for_details(user_message)

# Title
st.title("🤖 Build a RIG - AI-guided PC configurator")

# Context Panel - Always visible at top
budget_under = ""
if st.session_state.last_build_generated and st.session_state.total_cost > 0:
    remaining = st.session_state.current_budget - st.session_state.total_cost
    if remaining > 0:
        budget_under = f" (${remaining:.0f} under budget!)"
    else:
        budget_under = f" (${abs(remaining):.0f} over budget!)"

st.markdown(f"""
<div class="context-panel">
    <h3 style="margin: 0 0 10px 0;">🎯 Current Build Context</h3>
    <div class="quick-stats">
        <span><strong>💰 Budget:</strong> ${st.session_state.current_budget}</span>
        <span><strong>🎮 Use:</strong> {st.session_state.current_usage.title().replace('_', ' ')}</span>
        <span><strong>⚡ Status:</strong> {"✅ Build Generated" if st.session_state.last_build_generated else "⏳ Ready to Build"}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Build summary (if available)
if st.session_state.last_build_generated and st.session_state.total_cost > 0:
    st.markdown(f"""
    <div class="build-summary">
        <strong>🖥️ Last Generated Build:</strong> 
        Total Cost: <strong>${st.session_state.total_cost:.2f}</strong>
        <em style="color: {'#28a745' if budget_under and 'under' in budget_under else '#dc3545'};">{budget_under}</em>
    </div>
    """, unsafe_allow_html=True)

# Stylish tabs
tab1, tab2 = st.tabs(["📋 Build Configurator", "💬 AI Chat Assistant"])

with tab1:
    st.header("📋 PC Build Configurator")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Update session state when values change
        new_budget = st.slider("💰 Budget", 500, 10000, st.session_state.current_budget, 50)
        if new_budget != st.session_state.current_budget:
            st.session_state.current_budget = new_budget
        
        usage_options = {"Gaming": "gaming", "Design": "design", "Video Editing": "video_editing", "Office Work": "office_work"}
        selected_usage_display = st.selectbox("🎯 Primary Use", 
                                            list(usage_options.keys()),
                                            index=list(usage_options.values()).index(st.session_state.current_usage))
        new_usage = usage_options[selected_usage_display]
        if new_usage != st.session_state.current_usage:
            st.session_state.current_usage = new_usage
        
        # Advanced options in expander
        with st.expander("⚙️ Advanced Options"):
            st.selectbox("🎮 Target Resolution", ["1080p", "1440p", "4K"])
            st.selectbox("🎯 Target FPS", ["60 FPS", "120 FPS", "144+ FPS"])
            st.checkbox("🔄 Future-proof (add 20% budget)")
            st.checkbox("💡 RGB Lighting preferences")
        
    with col2:
        st.info("""
        **💡 Smart Recommendations:**
        
        🎮 **Gaming Focus**: Prioritize GPU performance
        
        🎨 **Creative Work**: Balance CPU + RAM
        
        🎬 **Video Editing**: High-end CPU + fast storage
        
        💼 **Office Work**: Efficient + quiet components
        """)
        
        # Quick preset buttons
        st.write("**⚡ Quick Presets:**")
        
        if st.button("🏆 Best Value Gaming", use_container_width=True):
            st.session_state.current_budget = 1200
            st.session_state.current_usage = "gaming"
            st.rerun()
            
        if st.button("🎨 Creative Workstation", use_container_width=True):
            st.session_state.current_budget = 2500
            st.session_state.current_usage = "design"
            st.rerun()
            
        if st.button("💼 Office Productivity", use_container_width=True):
            st.session_state.current_budget = 800
            st.session_state.current_usage = "office_work"
            st.rerun()
    
    # Generate build button
    if st.button("🚀 Generate Optimized Build", type="primary", use_container_width=True):
        message_container = st.empty()
        
        try:
            data = call_api_with_retry(st.session_state.current_budget, st.session_state.current_usage)
            
            st.session_state.current_build = data.get("build", {})
            st.session_state.candidates = data.get("candidates", {})
            st.session_state.explanation = data.get("explanation", "")
            st.session_state.last_build_generated = True
            update_build_and_cost()
            
            message_container.success("✅ Your PC build has been generated!")
            
        except Exception as exc:
            message_container.error(f"❌ {exc}")
            st.info("💡 If this persists, the API might be experiencing issues. Please try again in a few minutes.")
    
    # Display interactive build if available
    if st.session_state.current_build:
        st.markdown("---")
        st.subheader("🖥️ Your Recommended & Customizable Build")
        
        build_col1, build_col2 = st.columns([0.6, 0.4])
        
        with build_col1:
            st.write("**🔧 Customize Your Components**")
            build = st.session_state.current_build
            candidates = st.session_state.candidates
            
            for part_type, current_part in build.items():
                part_options = candidates.get(part_type, [])
                option_names = [p['name'] for p in part_options]
                
                try:
                    current_index = option_names.index(current_part['name'])
                except ValueError:
                    current_index = 0

                st.selectbox(
                    f"**{part_type.replace('_', ' ').title()}**",
                    options=option_names, index=current_index,
                    key=f"{part_type}_selector",
                    on_change=handle_part_change, args=(part_type,)
                )

                # Display details for the selected part
                sub_col1, sub_col2 = st.columns(2)
                sub_col1.metric("Price", f"${current_part.get('price', 0):.2f}")
                sub_col2.metric("Performance Score", f"{current_part.get('score', 0):,.0f}")
                st.divider()
        
        with build_col2:
            st.write("**📊 Build Analysis**")
            
            total_cost = st.session_state.get('total_cost', 0)
            st.metric("Total Estimated Cost", f"${total_cost:.2f}")
            
            if total_cost > st.session_state.current_budget:
                st.warning(f"Over budget by ${total_cost - st.session_state.current_budget:.2f}")
            else:
                st.success(f"Under budget by ${st.session_state.current_budget - total_cost:.2f}")

            # Compatibility check
            cpu = st.session_state.current_build.get("cpu", {})
            mobo = st.session_state.current_build.get("motherboard", {})
            if cpu.get("socket") != mobo.get("socket"):
                st.error(f"Socket Mismatch: CPU ({cpu.get('socket')}) & Motherboard ({mobo.get('socket')})")
            else:
                st.success("CPU and Motherboard are compatible.")
            
            st.write("**💬 AI Advisor's Explanation**")
            st.info(st.session_state.get('explanation', "No explanation available."))

with tab2:
    st.header("💬 AI Chat Assistant")
    st.markdown("Have a conversation about your PC building needs. Ask questions, get recommendations, and refine your build!")
    
    # Display chat history
    chat_container = st.container(height=450)
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Chat input with real AI processing
    if prompt := st.chat_input("Ask about PC builds, components, or get recommendations..."):
        # Add user message to history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Get AI response using real chat functionality
        with st.spinner("Analyzing your requirements..."):
            try:
                response = get_agent_response(prompt)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {e}"
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
        
        st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "👋 Hi! I'm your PC building expert. Tell me about what kind of computer you want to build - what's your budget and what will you use it for?"}
        ]
        st.rerun()

# Footer
st.markdown("---")
st.markdown("**Build a RIG** - AI-guided PC configurator with stylish contextual tabs") 