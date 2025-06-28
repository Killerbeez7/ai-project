from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from core.recommender import Recommender
from chains.llm_explainer import LLMExplainer
from data.data_loader import load_all_parts_data
from pathlib import Path

# --- Application Setup ---
app = FastAPI(
    title="Build a RIG API",
    description="An API to get custom PC build recommendations from an AI-guided PC configurator.",
    version="0.1.0",
)

# --- Data Models (Pydantic) ---
class Part(BaseModel):
    name: str
    price: float
    type: str

class BuildResponse(BaseModel):
    build: Dict[str, Part]
    explanation: str
    total_cost: float

# --- Global Resources ---
# Load data and initialize core components once at startup
data_path = Path("data/csv")
all_parts = load_all_parts_data(data_path)
recommender = Recommender(all_parts)
explainer = LLMExplainer()

# --- API Endpoints ---
@app.get("/build", response_model=BuildResponse)
def get_build(budget: float, usage: str = "gaming"):
    """
    Generates a PC build recommendation based on a budget and usage profile.
    """
    if budget < 500:
        raise HTTPException(
            status_code=400, 
            detail="Budget must be at least $500 to get a meaningful recommendation."
        )

    # 1. Get the core recommendation
    recommended_build = recommender.recommend(budget, usage)

    if not recommended_build:
        raise HTTPException(
            status_code=404, 
            detail=f"Could not generate a complete build for a ${budget} budget. Please try a higher amount."
        )

    # 2. Generate the explanation for the build
    explanation = explainer.generate_explanation(budget, usage, recommended_build)
    
    # 3. Calculate total cost and format the response
    total_cost = sum(part["price"] for part in recommended_build.values())
    
    # Ensure the build dictionary conforms to the Pydantic model
    formatted_build = {
        part_type: Part(**part_data) 
        for part_type, part_data in recommended_build.items()
    }

    return BuildResponse(
        build=formatted_build,
        explanation=explanation,
        total_cost=total_cost,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
