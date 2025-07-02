import streamlit as st

st.set_page_config(page_title="Layout Test 6: Stylish Contextual Tabs", layout="wide")

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

st.title("🖥️ Build a RIG - Layout Test 6: Stylish Contextual Tabs")

# Initialize persistent state
if 'current_budget' not in st.session_state:
    st.session_state.current_budget = 1500
if 'current_usage' not in st.session_state:
    st.session_state.current_usage = "gaming"
if 'last_build' not in st.session_state:
    st.session_state.last_build = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋 Hi! I'm your PC building expert. How can I help you today?"}
    ]

# Context Panel - Always visible at top
st.markdown("""
<div class="context-panel">
    <h3 style="margin: 0 0 10px 0;">🎯 Current Build Context</h3>
    <div class="quick-stats">
        <span><strong>💰 Budget:</strong> $""" + str(st.session_state.current_budget) + """</span>
        <span><strong>🎮 Use:</strong> """ + st.session_state.current_usage.title().replace('_', ' ') + """</span>
        <span><strong>⚡ Status:</strong> """ + ("✅ Build Generated" if st.session_state.last_build else "⏳ Ready to Build") + """</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Build summary (if available)
if st.session_state.last_build:
    st.markdown("""
    <div class="build-summary">
        <strong>🖥️ Last Generated Build:</strong> 
        Ryzen 5 7600X + RTX 4060 Ti + 16GB RAM + 1TB SSD = <strong>$969.96</strong>
        <em style="color: #28a745;">($""" + str(st.session_state.current_budget - 969.96) + """ under budget!)</em>
    </div>
    """, unsafe_allow_html=True)

# Stylish tabs
tab1, tab2 = st.tabs(["📋 Build Configurator", "💬 AI Chat Assistant"])

with tab1:
    st.header("📋 PC Build Configurator")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Update session state when values change
        new_budget = st.slider("💰 Budget", 500, 5000, st.session_state.current_budget, 50)
        if new_budget != st.session_state.current_budget:
            st.session_state.current_budget = new_budget
        
        new_usage = st.selectbox("🎯 Primary Use", 
                                ["gaming", "design", "video_editing", "office_work"],
                                index=["gaming", "design", "video_editing", "office_work"].index(st.session_state.current_usage))
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
        st.session_state.last_build = {
            "budget": st.session_state.current_budget,
            "usage": st.session_state.current_usage,
            "timestamp": "just now"
        }
        st.success(f"✅ Generated ${st.session_state.current_budget} {st.session_state.current_usage} build!")
        st.rerun()
    
    # Results display
    if st.session_state.last_build:
        st.markdown("---")
        st.subheader("🖥️ Your Optimized Build")
        
        # Interactive results with expandable details
        result_col1, result_col2, result_col3 = st.columns(3)
        
        with result_col1:
            with st.expander("🧠 **CPU** - Ryzen 5 7600X ($299.99)", expanded=True):
                st.write("• 6-core, 12-thread processor")
                st.write("• Excellent gaming performance")
                st.write("• Compatible with latest motherboards")
                st.progress(0.85)
                st.caption("Performance Score: 85/100")
            
            with st.expander("💾 **Memory** - 16GB DDR4 ($89.99)"):
                st.write("• 3200MHz speed")
                st.write("• Perfect for gaming & multitasking")
                st.write("• Expandable to 32GB")
                st.progress(0.80)
                st.caption("Performance Score: 80/100")
        
        with result_col2:
            with st.expander("🎮 **GPU** - RTX 4060 Ti ($499.99)", expanded=True):
                st.write("• Excellent 1440p gaming")
                st.write("• DLSS 3.0 support")
                st.write("• Ray tracing capable")
                st.progress(0.90)
                st.caption("Performance Score: 90/100")
            
            with st.expander("💿 **Storage** - 1TB NVMe ($79.99)"):
                st.write("• Fast PCIe 4.0 SSD")
                st.write("• 7000+ MB/s read speeds")
                st.write("• Perfect for gaming")
                st.progress(0.88)
                st.caption("Performance Score: 88/100")
        
        with result_col3:
            with st.expander("⚡ **PSU** - 650W Gold ($89.99)"):
                st.write("• 80+ Gold efficiency")
                st.write("• Fully modular cables")
                st.write("• 10-year warranty")
                st.progress(0.85)
                st.caption("Efficiency: 92%")
            
            with st.expander("📦 **Case** - Mid Tower ($69.99)"):
                st.write("• Excellent airflow design")
                st.write("• Tempered glass panel")
                st.write("• Tool-free installation")
                st.progress(0.75)
                st.caption("Build Quality: 75/100")

with tab2:
    st.header("💬 AI Chat Assistant")
    
    # Show current context in chat
    st.info(f"💡 **Current Context**: ${st.session_state.current_budget} {st.session_state.current_usage} build")
    
    chat_col1, chat_col2 = st.columns([3, 1])
    
    with chat_col1:
        # Chat history with context awareness
        chat_container = st.container(height=450)
        
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        
        # Chat input with context
        if prompt := st.chat_input(f"Ask about your ${st.session_state.current_budget} {st.session_state.current_usage} build..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Simulate AI response with context awareness
            context_response = f"Based on your ${st.session_state.current_budget} {st.session_state.current_usage} build: "
            
            if "upgrade" in prompt.lower():
                context_response += "I'd recommend upgrading the GPU to RTX 4070 for better performance. That would bring your total to about $1,169."
            elif "compatible" in prompt.lower():
                context_response += "Yes! All components in your current build are fully compatible. The Ryzen 5 7600X works perfectly with the RTX 4060 Ti."
            elif "cheaper" in prompt.lower():
                context_response += "We could save money by switching to GTX 1660 Super (-$200) or reducing RAM to 8GB (-$40). Would you like me to show alternatives?"
            else:
                context_response += "That's a great question! Your current build will handle most modern games at 1440p with 60+ FPS."
            
            st.session_state.chat_history.append({"role": "assistant", "content": context_response})
            st.rerun()
    
    with chat_col2:
        st.write("**🎯 Context-Aware Features:**")
        
        if st.button("🔄 Update Build Context"):
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": f"✅ Updated! Now discussing your ${st.session_state.current_budget} {st.session_state.current_usage} build."
            })
            st.rerun()
        
        if st.button("💡 Suggest Improvements"):
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"For your ${st.session_state.current_budget} {st.session_state.current_usage} build, I suggest: 1) Upgrade to RTX 4070 for future-proofing 2) Consider 32GB RAM for heavy workloads 3) Add CPU cooler for better temps"
            })
            st.rerun()
        
        if st.button("🔍 Compare Alternatives"):
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "Here are 3 alternatives for your budget: 1) Intel + RTX 4060 Ti 2) AMD + RTX 4070 3) Budget option with RTX 4060. Which interests you most?"
            })
            st.rerun()
        
        st.info("💬 **Chat remembers:**\n- Your current budget\n- Selected usage type\n- Generated builds\n- Previous questions")

# Footer
st.markdown("---")
st.markdown("**Layout 6:** Stylish contextual tabs - Context preserved across tabs, beautiful styling, persistent state") 