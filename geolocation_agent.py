import os
from pathlib import Path
from typing import Optional

from agno.agent import Agent
from agno.media import Image
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Define the query for geography identification
geo_query = """
You are a geography expert. Your task is to analyze the given image and provide a reasoned guess of the location based on visible clues such as:
- Landmarks
- Architecture
- Natural features (mountains, rivers, coastlines)
- Language or symbols (text, street signs, billboards, any names mentioned in the picture as clue)
- People's clothing or cultural aspects
- Environmental clues like weather, time of day

Return in this format:
Location Name, City, Country and Reasoning
Structure the response in markdown.

Instructions:
1. Examine the image thoroughly.
2. Provide a reasoned guess for the street name, city, state, and country.
3. Explain your reasoning in detail by pointing out the visual clues that led to your conclusion.
4. If uncertain, offer possible guesses with reasoning.
"""

def get_geo_agent():
    """
    Returns a Geolocation Agent configured with Gemini and DuckDuckGo tools.
    """
    geo_agent = Agent(
        name="Geolocation Agent",
        role="Analyze images to identify geographic locations",
        model=Gemini(id="gemini-2.0-flash-exp"), 
        tools=[DuckDuckGoTools()], 
        markdown=True,
        instructions="Analyze images to identify geographic locations based on visual clues.",
    )
    return geo_agent

# Function to analyze the image and return location information
def analyze_image(image_path: Path) -> Optional[str]:
    try:
        agent = get_geo_agent()
        response = agent.run(geo_query, images=[Image(filepath=image_path)])
        return response.content
    except Exception as e:
        raise RuntimeError(f"An error occurred while analyzing the image: {e}")