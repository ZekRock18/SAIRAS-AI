from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.yfinance import YFinanceTools

import os 
from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv('GROQ_API_KEY')

def get_finance_agent():
    """
    Returns a Financial Agent configured with Groq and YFinance tools.
    """
    finance_agent = Agent(
        name="Finance Agent",
        role="Provide financial data and analysis",
        add_history_to_messages=True,
        num_history_responses=3,
        model=Groq(id="qwen-2.5-32b"),
        tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
        instructions="Display data in tables when possible.",
        markdown=True,
        show_tool_calls=True,
    )
    return finance_agent

if __name__ == "__main__":
    agent = get_finance_agent()
    agent.print_response("Provide the latest financial data for AAPL.", stream=True)
