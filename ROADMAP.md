# Roadmap for building "PC Builder Assistant" web app

## Phase 1: MVP Implementation

### Project Setup & Dependencies
- [x] Create a new Python project and repository
- [x] Create a venv and install necessary packages: `pandas`, `NumPy`, `FastAPI`, `Uvicorn`, `LangChain`, `OpenAI API client`, `Streamlit`
- [x] Set up Git. Include `.gitignore` for env files, and prepare a `.env` file for secrets (like `OPENAI_API_KEY`)
- [x] Scaffold the project directories: `data/`, `src/`, `ui/`, `tests`, `notebooks`

### Data Ingestion & Preparation
- [x] Prepare the PC parts dataset and load it
- [x] Create or obtain a `parts.csv` file with columns like `part type`, `model name`, `price`, and `performance metric`
- [x] Use pandas to read the CSV into a DataFrame, ensuring correct data types
- [x] Set up a lightweight SQLite database

### Parts Recommendation Logic
- [x] Implement the core logic to suggest an optimal build
- [x] Filter available parts by the user's budget and criteria
- [x] Rank or select parts by a performance-to-price ratio using NumPy or pandas
- [x] Account for the usage parameter `gaming` / `design`
- [x] Ensure the total estimated price does not exceed the budget and handle cases where the budget is too low
- [x] Test the recommendation function with sample inputs to verify it returns sensible combinations

### LLM Integration
- [x] Integrate a LLM to explain the recommended build
- [x] Use LangChain to manage the prompt and OpenAI API call
- [x] Design a prompt that provides context to the LLM (role, budget, usage, selected parts)
- [x] Implement the prompt using LangChain's prompt templates
- [x] Keep the explanation concise and user-focused
- [x] Test the LLM call with sample data to ensure coherent and factual output
- [x] Ensure sensitive info (API keys) are handled via env variables

### API Backend (FastAPI)
- [x] Build a RESTful API to serve the recommendations
- [x] Set up a FastAPI app with an endpoint `GET /build`
- [x] Define data models using Pydantic for the response schema
- [x] Implement input validation for `budget` and `usage`
- [x] In the request handler, call the recommendation and LLM functions and return the results as JSON
- [x] Run the app with Uvicorn and test the endpoint manually

### User Interface (Streamlit App)
- [x] Develop a simple, user-friendly front-end
- [x] Create a Streamlit app with inputs for budget and usage
- [x] On submission, call the FastAPI endpoint to fetch the build and explanation
- [x] Display the results clearly on the Streamlit page (e.g.`st.table` and markdown)
- [x] Ensure the UI is clear, handles errors, and is responsive
- [x] Manually test the full app flow

### Testing & Documentation
- [x] Write basic unit tests for the parts recommendation logic using `pytest`
- [x] Add an integration test for the API using FastAPI's `TestClient`
- [x] Document the project in a `README.md` with setup instructions, example usage, and any assumptions made

## Phase 2: Additional Improvements

### Enhanced SQL Integration
- [x] Integrate a proper database layer `SQLite` or `PostgreSQL` to handle larger datasets more efficiently
- [x] Use SQL queries to fetch parts

### Advanced Recommendation Logic
- [x] Include compatibility checks (CPU socket vs. motherboard)
- [x] Use a more sophisticated algorithm to optimize budget allocation across components
- [x] Expand usage profiles (`Video Editing`, `Office Work`) with different part priorities

### Data and LLM Enhancements
- [ ] Incorporate real-world data via external APIs or web-scraping for up-to-date prices
- [ ] Use RAG approach for more detailed and factual LLM explanations
- [ ] Allow the user to choose the level of detail in the explanation

### UI/UX Improvements
- [x] Add enhanced input validation and helpful hints in the Streamlit UI
- [x] Make the UI more interactive, allowing users to manually adjust the build
- [ ] Deploy the app to a cloud service (Streamlit Community Cloud)

### Testing & DevOps
- [ ] Increase test coverage and integrate continuous integration (GitHub Actions)
- [ ] Consider performance testing and add monitoring/analytics if the app is deployed as a service