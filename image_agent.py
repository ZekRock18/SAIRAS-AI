from agno.agent import Agent
from agno.media import Image
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.google import Gemini
import os 
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_API_KEY"]=os.getenv('GOOGLE_API_KEY')

def get_image_agent():
    """
    Creates and returns an image analysis agent.
        
    Returns:
        Agent: An agent configured for image analysis.
    """
    image_agent = Agent(
        name="Image Analyzer",
        model=Gemini(id="gemini-2.0-flash-exp"),  # Gemini handles images natively
        tools=[DuckDuckGoTools()],
        role="Analyze images and provide detailed information about them",
        instructions=[
            "Analyze the provided image in detail",
            "Identify key elements, objects, and context in the image",
            "If relevant, search for the latest news about the subject of the image",
            "Provide a comprehensive analysis with context and background information",
            "Always respond to the specific query about the image"
        ],
        markdown=True,
    )
    
    return image_agent

def analyze_image(image_url, query="Tell me about this image"):
    """
    Analyze an image using the image agent.
    
    Args:
        image_url (str): URL of the image to analyze.
        query (str): Specific query about the image. Defaults to a general request.
        
    Returns:
        RunResponse: The response from the image agent.
    """
    try:
        agent = get_image_agent()
        response = agent.run(
            query,
            images=[Image(url=image_url)],
            stream=False
        )
        return response
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return f"Error analyzing image: {str(e)}"

