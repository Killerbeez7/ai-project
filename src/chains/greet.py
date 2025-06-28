from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

_llm = ChatOpenAI(model="gpt-4o-mini")

_prompt = PromptTemplate(
    template="You are an upbeat data assistant.\n"
             "User name: {name}\n"
             "Return a brief, friendly greeting.",
    input_variables=["name"],
)

hello_chain = _prompt | _llm | StrOutputParser()

def say_hello(name: str) -> str:
    """Return a friendly LLM-generated greeting."""
    return hello_chain.invoke({"name": name})


if __name__ == "__main__":
    """Run the chain when the script is executed directly."""
    print(say_hello("Developer"))
