import streamlit as st
import requests

# page config
st.set_page_config(
    page_title="Build a RIG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# app state init
def init_session_state():
    """Initializes session state variables if they don't exist."""
    state_defaults = {
        'current_build': {},
        'candidates': {},
        'explanation': "",
        'total_cost': 0.0,
        'initial_budget': 1500,
    }
    for key, value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# helper functions
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

# ui rendering
st.title("🤖 Build a RIG | AI-guided PC configurator")
st.markdown("Welcome! Tell us your budget and primary use case, and our AI assistant will recommend the perfect PC build for you.")
st.divider()

# API Configuration
API_BASE_URL = "https://build-a-rig.vercel.app"

# User Inputs
st.header("1. Enter Your Requirements")
col1, col2 = st.columns(2)
with col1:
    budget = st.number_input(
        "**What is your budget ($)?**", 
        min_value=500, max_value=10000, value=st.session_state.initial_budget, step=100,
        help="Enter a budget between $500 and $10,000."
    )

with col2:
    usage_options = {"Gaming": "gaming", "Design": "design", "Video Editing": "video_editing", "Office Work": "office_work"}
    selected_usage_display = st.selectbox(
        "**What is the primary use for this PC?**",
        list(usage_options.keys()), index=0,
        help="Select the main activity you'll be using this PC for."
    )
    usage = usage_options[selected_usage_display]

st.divider()

# recommendation trigger
if st.button("🚀 Generate My PC Build", type="primary", use_container_width=True):
    st.session_state.initial_budget = budget  # Store the budget for comparison
    api_url = f"{API_BASE_URL}/build"
    params = {"budget": budget, "usage": usage}

    with st.spinner("🔍 Analyzing parts, running combinations, and asking the AI for advice..."):
        try:
            response = requests.get(api_url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            st.session_state.current_build = data.get("build", {})
            st.session_state.candidates = data.get("candidates", {})
            st.session_state.explanation = data.get("explanation", "")
            update_build_and_cost()
        except requests.HTTPError as http_err:
            try:
                error_detail = http_err.response.json().get("detail", "An unknown error occurred.")
            except:
                error_detail = http_err.response.text
            st.error(f"Error from API: {error_detail}")
        except requests.RequestException as e:
            st.error(f"Failed to connect to the recommendation API: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# display interactive build
if st.session_state.current_build:
    st.header("2. Your Recommended & Customizable Build")
    
    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        st.subheader("🖥️ Customize Your Components")
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

            # display details for the selected part
            sub_col1, sub_col2 = st.columns(2)
            sub_col1.metric("Price", f"${current_part.get('price', 0):.2f}")
            sub_col2.metric("Performance Score", f"{current_part.get('score', 0):,.0f}")
            st.divider()

    with col2:
        st.subheader("📊 Build Analysis")
        
        total_cost = st.session_state.get('total_cost', 0)
        st.metric("Total Estimated Cost", f"${total_cost:.2f}")
        
        if total_cost > st.session_state.initial_budget:
            st.warning(f"Over budget by ${total_cost - st.session_state.initial_budget:.2f}")

        # compatibility check
        cpu = st.session_state.current_build.get("cpu", {})
        mobo = st.session_state.current_build.get("motherboard", {})
        if cpu.get("socket") != mobo.get("socket"):
            st.error(f"Socket Mismatch: CPU ({cpu.get('socket')}) & Motherboard ({mobo.get('socket')})")
        else:
            st.success("CPU and Motherboard are compatible.")
        
        st.subheader("💬 AI Advisor's Explanation")
        st.info(st.session_state.get('explanation', "No explanation available.")) 