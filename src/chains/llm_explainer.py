from typing import Dict, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


# Handles generating a natural language explanation for a recommended PC build.
class LLMExplainer:

    PROMPT_TEMPLATE: str = """
    You are an expert PC hardware advisor.
    A user has requested a PC build with the following specifications:
    - Budget: ${budget}
    - Primary Use: {usage}

    The following build was recommended:
    {build_details}

    Please provide a brief, friendly, and encouraging explanation (around 100-150 words)
    of why this is a good build for the user's needs. Highlight why the key components
    (especially the CPU and GPU) are a great fit for the intended usage and budget.
    Mention any smart trade-offs that were made to meet the budget.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        load_dotenv()
        self.model_name = model_name
        self._llm = ChatOpenAI(model=self.model_name, temperature=0.7)
        self._prompt = PromptTemplate.from_template(self.PROMPT_TEMPLATE)
        self._chain = self._prompt | self._llm | StrOutputParser()

    # Formats the build dictionary into a readable string for the prompt
    def _format_build_details(self, build: Dict[str, Any]) -> str:
        details = []
        for part_type, part_info in build.items():
            name = part_info.get("name", "N/A")
            price = part_info.get("price", 0)
            details.append(
                f"- {part_type.replace('_', ' ').title()}: {name} (${price:.2f})"
            )
        return "\n".join(details)

    # Generates an explanation for the given build
    def generate_explanation(
        self, budget: float, usage: str, build: Dict[str, Any]
    ) -> str:
        build_details = self._format_build_details(build)
        explanation = self._chain.invoke(
            {
                "budget": budget,
                "usage": usage,
                "build_details": build_details,
            }
        )
        return explanation


if __name__ == "__main__":
    from src.core.recommender import Recommender
    from src.data.data_loader import load_all_parts_data
    from pathlib import Path

    # Load data and get a sample recommendation
    data_path = Path("data/csv")
    all_parts = load_all_parts_data(data_path)

    if not all_parts.empty:
        recommender = Recommender(all_parts)
        test_budget = 1500.00
        test_usage = "gaming"
        recommended_build = recommender.recommend(test_budget, test_usage)

        if recommended_build:
            print("--- Generating explanation for the following build: ---")
            total_cost = 0
            for part_type, part_info in recommended_build.items():
                price = part_info.get("price", 0)
                total_cost += price
                print(
                    f"- {part_type.replace('_', ' ').title()}: {part_info.get('name')} (${price:.2f})"
                )
            print(f"\nTotal Estimated Cost: ${total_cost:.2f}\n" + "=" * 50)

            # Generate the explanation
            explainer = LLMExplainer()
            explanation = explainer.generate_explanation(
                test_budget, test_usage, recommended_build
            )

            print("\n--- LLM-Generated Explanation ---")
            print(explanation)
        else:
            print("Could not generate a build to explain.")
