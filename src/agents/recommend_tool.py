"""
LangChain tool for PC build recommendations.
Converts the Python recommender into an OpenAI function-calling tool.
"""

from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Dict, Any, Tuple, List
from pathlib import Path
import json
import os

from src.core.recommender import Recommender
from src.data.data_loader import load_all_parts_data

_parts_data = None
_recommender = None


def get_recommender() -> Recommender:
    """Lazy loading of recommender to avoid issues during import."""
    global _parts_data, _recommender

    if _recommender is None:
        data_path = Path(__file__).parents[2] / "data" / "parts.db"
        _parts_data = load_all_parts_data(data_path)
        _recommender = Recommender(_parts_data)

    return _recommender


class BuildArgs(BaseModel):
    """Arguments for the PC build recommendation tool."""

    budget: float = Field(
        ...,
        gt=500,
        le=10000,
        description="Total budget in USD (minimum $500, maximum $10,000)",
    )
    usage: str = Field(
        ...,
        pattern="^(gaming|design|video_editing|office_work)$",
        description="Primary use case: gaming, design, video_editing, or office_work",
    )


@tool("recommend_pc_build", args_schema=BuildArgs)
def recommend_pc_build(budget: float, usage: str) -> str:
    """
    Generate a complete PC build recommendation within the specified budget.

    This tool analyzes component compatibility, performance requirements,
    and budget constraints to recommend an optimal PC configuration.

    Args:
        budget: Total budget in USD (500-10000)
        usage: Primary use case (gaming|design|video_editing|office_work)

    Returns:
        JSON string containing the complete build recommendation with explanation
    """
    try:
        recommender = get_recommender()

        build, candidates = recommender.recommend(budget, usage)

        if not build:
            return json.dumps(
                {
                    "error": f"Could not generate a complete build for ${budget} budget",
                    "suggestion": "Try increasing the budget or selecting a different use case",
                }
            )

        total_cost = sum(part["price"] for part in build.values())

        response = {
            "build": build,
            "total_cost": total_cost,
            "budget": budget,
            "usage": usage,
            "candidates": {
                part_type: len(part_list) for part_type, part_list in candidates.items()
            },
            "compatibility_check": {
                "cpu_socket": build.get("cpu", {}).get("socket"),
                "motherboard_socket": build.get("motherboard", {}).get("socket"),
                "compatible": build.get("cpu", {}).get("socket")
                == build.get("motherboard", {}).get("socket"),
            },
        }

        return json.dumps(response, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Error generating PC build: {str(e)}",
                "budget": budget,
                "usage": usage,
            }
        )


@tool("get_component_options")
def get_component_options(component_type: str, max_price: float = None) -> str:
    """
    Get available options for a specific PC component type.

    Args:
        component_type: Type of component (cpu, gpu, motherboard, etc.)
        max_price: Optional maximum price filter

    Returns:
        JSON string with available component options
    """
    try:
        recommender = get_recommender()

        components = recommender.parts_df[
            recommender.parts_df["type"] == component_type
        ]

        if max_price:
            components = components[components["price"] <= max_price]

        top_components = components.nlargest(10, "score")

        result = {
            "component_type": component_type,
            "max_price": max_price,
            "options": top_components.to_dict("records"),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Error getting component options: {str(e)}",
                "component_type": component_type,
            }
        )


# Export the tools for use in agents
__all__ = ["recommend_pc_build", "get_component_options", "BuildArgs"]
