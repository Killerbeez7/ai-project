import streamlit as st
import requests
import os
import time

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
try:
    API_URL = st.secrets["API_URL"]
except (KeyError, FileNotFoundError):
    API_URL = os.environ.get("API_URL", "http://localhost:8000")

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

# helper function for API calls with cold start handling
def call_api_with_retry(budget, usage):
    """
    Calls the API with retry logic to handle cold starts gracefully.
    Tries immediately, then retries after 5 seconds if we get a 502 error.
    """
    params = {"budget": budget, "usage": usage}
    api_url = f"{API_URL}/v1/build"
    
    for attempt, delay in enumerate([(0, "🔍 Analyzing parts, running combinations, and asking the AI for advice..."), 
                                     (5, "⏳ API is warming up (cold start), please wait...")], 1):
        sleep_time, message = delay
        
        if sleep_time > 0:
            # Show different message for retry
            with st.spinner(message):
                time.sleep(sleep_time)
        
        try:
            with st.spinner(message):
                response = requests.get(api_url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()  # SUCCESS!
                
        except requests.HTTPError as http_err:
            # Check if it's a 502 error and we haven't retried yet
            if response.status_code == 502 and attempt == 1:
                st.info("🔄 Server is starting up (cold start). Retrying in 5 seconds...")
                continue  # Try again with delay
            
            # For other HTTP errors or if we've already retried
            try:
                error_detail = http_err.response.json().get("detail", "An unknown error occurred.")
            except:
                error_detail = http_err.response.text
            raise Exception(f"API Error ({response.status_code}): {error_detail}")
            
        except requests.RequestException as e:
            if attempt == 1:
                st.info("🔄 Connection issue. Retrying in 5 seconds...")
                continue  # Try again with delay
            raise Exception(f"Failed to connect to the recommendation API: {e}")
    
    raise Exception("API request failed after retries")

# recommendation trigger
if st.button("🚀 Generate My PC Build", type="primary", use_container_width=True):
    st.session_state.initial_budget = budget  # Store the budget for comparison
    
    try:
        data = call_api_with_retry(budget, usage)
        
        st.session_state.current_build = data.get("build", {})
        st.session_state.candidates = data.get("candidates", {})
        st.session_state.explanation = data.get("explanation", "")
        update_build_and_cost()
        
        # Show success message briefly
        st.success("✅ Your PC build has been generated!")
        
    except Exception as exc:
        st.error(f"❌ {exc}")
        st.info("💡 If this persists, the API might be experiencing issues. Please try again in a few minutes.")

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