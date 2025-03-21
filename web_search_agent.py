from agno.agent import Agent

from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
import os 
from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv('GROQ_API_KEY')



def get_web_agent():
    """
    Returns a WebSearch Agent configured with Groq and the DuckDuckGo tool.
    """
    web_agent = Agent(
        name="Web Agent",
        role="Search the web for up-to-date information",
        model=Groq(id="qwen-2.5-32b"),
        add_history_to_messages=True,
        num_history_responses=3,
        tools=[DuckDuckGoTools()],
        instructions="Always include sources in your responses.",
        markdown=True,
        show_tool_calls=True,
    
    )
    return web_agent

