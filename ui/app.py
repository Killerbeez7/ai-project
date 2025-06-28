import streamlit as st
import requests
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Build a RIG",
    page_icon="🤖",
    layout="wide",
)

# --- App Title and Description ---
st.title("Build a RIG | AI-guided PC configurator")
st.markdown(
    "Welcome! Tell us your budget and primary use case, and our AI assistant will recommend the perfect PC build for you."
)

# --- API Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- User Inputs ---
st.header("1. Enter Your Requirements")
col1, col2 = st.columns(2)
with col1:
    budget = st.number_input(
        "What is your budget ($)?", 
        min_value=500, 
        max_value=10000, 
        value=1500, 
        step=100,
        help="Enter a budget between $500 and $10,000."
    )

with col2:
    usage = st.selectbox(
        "What is the primary use for this PC?",
        ("Gaming", "Design", "Video Editing", "Office Work"),
        index=0,
        help="Select the main activity you'll be using this PC for."
    )
    usage = usage.lower()

# --- Recommendation Trigger ---
if st.button("🚀 Generate My PC Build", type="primary"):
    st.header("2. Your Recommended Build")

    # Call the FastAPI backend
    api_url = f"{API_BASE_URL}/build"
    params = {"budget": budget, "usage": usage}

    with st.spinner("🔍 Analyzing parts and asking the AI for advice..."):
        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            
            data = response.json()

            # --- Display Results ---
            st.subheader("Component List")
            
            build_data = data.get("build", {})
            parts_list = [
                {
                    "Component": part["type"].replace("_", " ").title(),
                    "Part Name": part["name"],
                    "Price ($)": f"{part['price']:.2f}",
                }
                for part in build_data.values()
            ]
            
            df = pd.DataFrame(parts_list)
            st.table(df)

            st.subheader("Total Estimated Cost")
            total_cost = data.get("total_cost", 0)
            st.success(f"**${total_cost:.2f}**")

            st.subheader("AI Advisor's Explanation")
            explanation = data.get("explanation", "No explanation available.")
            st.markdown(explanation)

        except requests.exceptions.HTTPError as http_err:
            error_detail = http_err.response.json().get("detail", "An unknown error occurred.")
            st.error(f"Error: {error_detail}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to the recommendation API. Please ensure the backend server is running. Details: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}") 