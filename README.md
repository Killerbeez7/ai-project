# Build a RIG | AI-guided PC configurator

This project is a web application that helps users build a custom PC. Users can specify a budget and primary usage (e.g., Gaming, Design), and the application will recommend a full set of compatible components. It also uses a Large Language Model (LLM) to provide a natural language explanation of why the build is a good fit for the user's needs.

## Tech Stack

- **Backend:** FastAPI, Uvicorn
- **Frontend:** Streamlit
- **AI/ML:** LangChain, OpenAI
- **Data Handling:** Pandas, NumPy
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
The API will be available at `http://127.0.0.1:8000`. You can see the interactive documentation at `http://127.0.0.1:8000/docs`.

### 2. Run the Frontend UI

In a second terminal, run the following command to start the Streamlit application:

```bash
streamlit run ui/app.py
```
This will open the user interface in your default web browser.
