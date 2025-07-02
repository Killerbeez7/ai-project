"""
LangChain agent for PC build consultation.
Uses the recommend_tool to provide conversational PC build assistance.
"""

from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage
from typing import Dict, Any, List

from .recommend_tool import recommend_pc_build, get_component_options


class PCBuildAgent:
    """
    Conversational AI agent for PC build recommendations.

    This agent can:
    - Understand natural language requests for PC builds
    - Ask clarifying questions about budget and usage
    - Provide detailed explanations and alternatives
    - Help users understand component choices
    """

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.tools = [recommend_pc_build, get_component_options]

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a knowledgeable PC building expert and consultant. 
            Your goal is to help users build the perfect PC for their needs and budget.
            
            You have access to tools that can:
            1. Generate complete PC build recommendations
            2. Look up specific component options
            
            Guidelines:
            - Always ask about budget and primary use case if not provided
            - Explain component choices in simple terms
            - Mention compatibility considerations (especially CPU/motherboard sockets)
            - Suggest alternatives if the budget is too low for their needs
            - Be encouraging and educational
            - If a build seems over/under budget, explain why and suggest adjustments
            
            Use case mappings:
            - Gaming: Prioritizes GPU performance, good CPU, adequate RAM
            - Design: Balanced CPU/GPU, more RAM, professional features
            - Video Editing: Strong CPU, lots of RAM, fast storage
            - Office Work: Budget-friendly, efficient, reliable components
            """,
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

        self.chat_history: List[Any] = []

    def chat(self, user_input: str) -> str:
        """
        Process a user message and return the agent's response.

        Args:
            user_input: The user's message/question

        Returns:
            The agent's response as a string
        """
        try:
            result = self.executor.invoke(
                {"input": user_input, "chat_history": self.chat_history}
            )

            self.chat_history.extend(
                [HumanMessage(content=user_input), AIMessage(content=result["output"])]
            )

            return result["output"]

        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}. Please try rephrasing your question."

            self.chat_history.extend(
                [HumanMessage(content=user_input), AIMessage(content=error_msg)]
            )

            return error_msg

    def reset_conversation(self):
        """Clear the chat history to start a new conversation."""
        self.chat_history = []

    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        if not self.chat_history:
            return "No conversation history yet."

        summary = "Conversation Summary:\n"
        for i, message in enumerate(self.chat_history[-6:]):  # Last 6 messages
            role = "User" if isinstance(message, HumanMessage) else "Assistant"
            content = (
                message.content[:100] + "..."
                if len(message.content) > 100
                else message.content
            )
            summary += f"{role}: {content}\n"

        return summary


# Example usage function
def create_build_consultation_agent() -> PCBuildAgent:
    """Factory function to create a PC build consultation agent."""
    return PCBuildAgent(model_name="gpt-4", temperature=0.7)


# Simple function interface for backward compatibility
def get_ai_build_recommendation(
    user_query: str, budget: float = None, usage: str = None
) -> str:
    """
    Simple function interface that uses the agent for one-off recommendations.

    Args:
        user_query: Natural language query about PC building
        budget: Optional budget hint
        usage: Optional usage hint

    Returns:
        AI response as string
    """
    agent = create_build_consultation_agent()

    # Enhance the query with budget/usage if provided
    enhanced_query = user_query
    if budget:
        enhanced_query += f" My budget is ${budget}."
    if usage:
        enhanced_query += f" I primarily need this for {usage}."

    return agent.chat(enhanced_query)
