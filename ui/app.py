import streamlit as st
import requests
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Build a RIG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Custom CSS for styling ---
st.markdown("""
<style>
    .stNumberInput, .stSelectbox {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
    }
    .stSpinner > div > div {
        border-top-color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# --- App Title and Description ---
st.title("🤖 Build a RIG | AI-guided PC configurator")
st.markdown(
    "Welcome! Tell us your budget and primary use case, and our AI assistant will recommend the perfect PC build for you."
)
st.divider()

# --- API Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- User Inputs ---
st.header("1. Enter Your Requirements")
col1, col2 = st.columns(2)
with col1:
    budget = st.number_input(
        "**What is your budget ($)?**", 
        min_value=500, 
        max_value=10000, 
        value=1500, 
        step=100,
        help="Enter a budget between $500 and $10,000."
    )

with col2:
    usage_options = {
        "Gaming": "gaming",
        "Design": "design",
        "Video Editing": "gaming", # Using gaming weights as a proxy for now
        "Office Work": "design", # Using design weights as a proxy for now
    }
    selected_usage_display = st.selectbox(
        "**What is the primary use for this PC?**",
        list(usage_options.keys()),
        index=0,
        help="Select the main activity you'll be using this PC for."
    )
    usage = usage_options[selected_usage_display]

st.divider()

# --- Recommendation Trigger ---
if st.button("🚀 Generate My PC Build", type="primary"):
    st.header("2. Your Recommended Build")

    api_url = f"{API_BASE_URL}/build"
    params = {"budget": budget, "usage": usage}

    with st.spinner("🔍 Analyzing parts, running combinations, and asking the AI for advice... This might take a moment!"):
        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            
            data = response.json()

            # --- Display Results ---
            col1, col2 = st.columns([0.6, 0.4])

            with col1:
                st.subheader("🖥️ Component List")
                build = data.get("build", {})
                if not build:
                    st.warning("Could not generate a build for the given budget and usage. Please try adjusting the budget.")
                else:
                    for part_type, part in build.items():
                        expander = st.expander(f"**{part['type'].replace('_', ' ').title()}** | {part['name']}")
                        expander.metric("Price", f"${part['price']:.2f}")
                        expander.metric("Performance Score", f"{part.get('score', 'N/A')}")
                        if part['type'] in ['cpu', 'motherboard'] and 'socket' in part:
                             expander.write(f"Socket: {part['socket']}")
            
            with col2:
                st.subheader("📊 Build Summary")
                total_cost = data.get("total_cost", 0)
                
                st.metric("Total Estimated Cost", f"${total_cost:.2f}")
                
                # Calculate and display total synergy score
                total_score = sum(p.get("score", 0) for p in data.get("build", {}).values())
                st.metric("Total Performance Score", f"{total_score:,.0f}")
                
                st.subheader("💬 AI Advisor's Explanation")
                st.info(data.get("explanation", "No explanation available."))


        except requests.exceptions.HTTPError as http_err:
            try:
                error_detail = http_err.response.json().get("detail", "An unknown error occurred.")
            except:
                error_detail = http_err.response.text
            st.error(f"Error from API: {error_detail}")
        except requests.exceptions.RequestException:
            st.error("Failed to connect to the recommendation API. Please make sure the backend server is running and accessible.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}") 