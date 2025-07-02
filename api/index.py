from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from pathlib import Path
import sys

# Add the parent directory to the path so we can import from src
sys.path.append(str(Path(__file__).parent.parent))

from src.core.recommender import Recommender
from src.chains.llm_explainer import LLMExplainer
from src.data.data_loader import load_all_parts_data

# Create FastAPI application
app = FastAPI(
    title="Build a RIG API",
    description="An AI-guided PC configurator that recommends custom PC builds based on budget and usage.",
    version="1.0.0",
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
)

# Data Models
class Part(BaseModel):
    name: str
    price: float
    type: str
    score: float
    socket: str | None = None

class BuildResponse(BaseModel):
    build: Dict[str, Part]
    explanation: str
    total_cost: float
    candidates: Dict[str, List[Part]]

# Initialize global resources
data_path = Path(__file__).parent.parent / "data" / "parts.db"
all_parts = load_all_parts_data(data_path)
recommender = Recommender(all_parts)
explainer = LLMExplainer()

@app.get("/")
def root():
    """Root endpoint for the API."""
    return {"message": "Build a RIG API is running!", "docs": "/v1/docs", "version": "v1"}

@app.get("/health")
def health():
    """Health check endpoint for Render."""
    return {"status": "healthy"}

@app.get("/v1/build", response_model=BuildResponse)
def get_build(budget: float, usage: str = "gaming"):
    """
    Generates a PC build recommendation based on a budget and usage profile.
    
    Args:
        budget: The budget for the PC build in USD
        usage: The primary use case (gaming, design, video_editing, office_work)
    
    Returns:
        BuildResponse: Complete build recommendation with explanation and alternatives
    """
    if budget < 800:
        raise HTTPException(
            status_code=400, 
            detail="Budget must be at least $800 to build a complete PC. Our data shows the minimum working build costs $798."
        )

    # Get the core recommendation and candidates
    recommended_build, candidates = recommender.recommend(budget, usage)

    if not recommended_build:
        raise HTTPException(
            status_code=404, 
            detail=f"Could not generate a complete build for a ${budget} budget. Please try a higher amount."
        )

    # Generate the explanation for the build
    explanation = explainer.generate_explanation(budget, usage, recommended_build)
    
    # Calculate total cost and format the response
    total_cost = sum(part["price"] for part in recommended_build.values())
    
    # Ensure the build dictionary conforms to the Pydantic model
    formatted_build = {
        part_type: Part(**part_data) 
        for part_type, part_data in recommended_build.items()
    }

    # Ensure the candidates dictionary conforms to the Pydantic model
    formatted_candidates = {
        part_type: [Part(**part_data) for part_data in part_list]
        for part_type, part_list in candidates.items()
    }

    return BuildResponse(
        build=formatted_build,
        explanation=explanation,
        total_cost=total_cost,
        candidates=formatted_candidates,
    ) 