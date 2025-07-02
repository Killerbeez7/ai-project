# Build a RIG | AI-guided PC configurator

This project is a web application that helps users build a custom PC. Users can specify a budget and primary usage (e.g., Gaming, Design), and the application will recommend a full set of compatible components. It also uses a Large Language Model (LLM) to provide a natural language explanation of why the build is a good fit for the user's needs.

## Live Demo

- **Frontend (UI):** Coming soon
- **Backend (API):** [https://build-a-rig.onrender.com](https://build-a-rig.onrender.com)
- **API Documentation:** [https://build-a-rig.onrender.com/v1/docs](https://build-a-rig.onrender.com/v1/docs)

## Features

- **AI-Powered Recommendations:** Uses OpenAI GPT models to generate personalized PC build explanations
- **Component Compatibility:** Automatically ensures CPU and motherboard socket compatibility
- **Budget Optimization:** Finds the best components within your specified budget
- **Usage-Specific Builds:** Optimizes builds for Gaming, Design, Video Editing, or Office Work
- **Interactive Customization:** Swap components and see real-time price and compatibility updates
- **Cold Start Handling:** Graceful loading states during server startup
- **API Versioning:** Future-proof REST API with v1 namespace

## Tech Stack

- **Backend:** FastAPI, Uvicorn (Python 3.11)
- **Frontend:** Streamlit
- **AI/ML:** LangChain, OpenAI GPT-4
- **Data Handling:** Pandas, NumPy, SQLite
- **Deployment:** Render.com
- **Testing:** Pytest

## Setup and Installation

Instructions to set up and run the project locally after cloning from GitHub.

### 1. Create and Activate Virtual Environment

It's recommended to use a virtual environment to manage project dependencies.

```bash
# Create the virtual environment
python -m venv .venv

# Activate the environment (Windows)
.venv\Scripts\activate

# Activate the environment (macOS/Linux)
source .venv/bin/activate
```

### 2. Install Dependencies

Install dependencies for both the API and UI:

```bash
# Install API dependencies
pip install -r api/requirements.txt

# Install UI dependencies  
pip install -r ui/requirements.txt

# Or install all development dependencies (includes everything)
pip install -r requirements.dev.txt
```

### 3. Set Up Environment Variables

The project requires an OpenAI API key.

- Make a copy of the `.env.example` file and name it `.env`.
- Open the `.env` file and add your OpenAI API key.

```
OPENAI_API_KEY="sk-..."
```

### 4. Install Project in Editable Mode

This step makes the project's source code importable across the application.

```bash
pip install -e .
```

## How to Run

This application consists of two main parts that must be run in separate terminals: the FastAPI backend and the Streamlit frontend.

### 1. Run the Backend API

In your first terminal, run the following command from the project root to start the FastAPI server:

```bash
uvicorn api.index:app --reload
```
The API will be available at `http://127.0.0.1:8000`. You can see the interactive documentation at `http://127.0.0.1:8000/v1/docs`.

### 2. Run the Frontend UI

In a second terminal, run the following command to start the Streamlit application:

```bash
streamlit run ui/app.py
```
This will open the user interface in your default web browser.

## Project Structure

```
build-a-rig/
├── api/                     # FastAPI backend
│   ├── index.py           # Main API application with v1 endpoints
│   └── requirements.txt   # Backend-only dependencies
├── ui/                      # Streamlit frontend
│   ├── app.py             # Main UI application with cold start handling
│   └── requirements.txt   # Frontend-only dependencies  
├── src/                     # Core business logic
│   ├── core/              # Recommendation engine
│   ├── chains/            # LLM integration
│   └── data/              # Data loading and processing
├── data/                    # Database and CSV files
├── render.yaml            # Deployment configuration
└── requirements.dev.txt   # All dependencies for local development
```

## API Endpoints

The API is versioned and available at the base URL: `https://build-a-rig.onrender.com`

### Core Endpoints

- **`GET /`** - API status and version info
- **`GET /health`** - Health check endpoint
- **`GET /v1/build`** - Generate PC build recommendation

### API Documentation

- **Interactive Docs:** `/v1/docs` (Swagger UI)
- **Alternative Docs:** `/v1/redoc` (ReDoc)

### Example API Usage

```bash
# Get a gaming build for $1500 budget
curl "https://build-a-rig.onrender.com/v1/build?budget=1500&usage=gaming"

# Get a design workstation for $2000 budget  
curl "https://build-a-rig.onrender.com/v1/build?budget=2000&usage=design"
```

## Key Features Explained

### Cold Start Handling
The UI automatically handles server cold starts with:
- Immediate retry for 502 errors
- User-friendly loading messages
- Graceful fallback for connection issues

### API Versioning
All endpoints are versioned under `/v1/` to ensure:
- Future compatibility when adding new features
- Smooth migration paths for API updates
- Clear documentation separation by version

### Smart Component Matching
The recommendation engine:
- Ensures CPU and motherboard socket compatibility
- Optimizes price-to-performance ratios
- Considers usage-specific requirements (gaming vs. productivity)

### LangChain Integration
Advanced AI agent capabilities:
- **Function Calling Tools:** PC recommender exposed as LangChain tools
- **Conversational Agent:** Natural language PC building consultation
- **Multi-turn Conversations:** Context-aware dialogue for complex requirements
- **Component Research:** AI-powered component option exploration

## Deployment

This project is configured for deployment on [Render.com](https://render.com) using the included `render.yaml` blueprint.

### Environment Variables

**API Service:**
- `OPENAI_API_KEY` - Your OpenAI API key

**UI Service:**
- `API_URL` - Automatically set to the API service URL by Render

### Manual Deployment

1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Blueprint and select this repository
4. Add your `OPENAI_API_KEY` to the API service environment variables
5. Deploy!

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src

# Run linting
ruff check .
```
