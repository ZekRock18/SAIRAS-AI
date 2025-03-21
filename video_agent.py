from agno.agent import Agent
from agno.media import Video
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.google import Gemini
import os 
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
os.environ["GOOGLE_API_KEY"]=os.getenv('GOOGLE_API_KEY')

def get_video_agent():
    """
    Creates and returns a video analysis agent.
        
    Returns:
        Agent: An agent configured for video analysis.
    """
    video_agent = Agent(
        name="Video Analyzer",
        model=Gemini(id="gemini-2.0-flash-exp"),  # Gemini handles videos natively
        tools=[DuckDuckGoTools()],
        role="Analyze videos and provide detailed information about them",
        instructions=[
            "Analyze the provided video in detail",
            "Identify key elements, objects, and context in the video",
            "If relevant, search for the latest news about the subject of the video",
            "Provide a comprehensive analysis with context and background information",
            "Always respond to the specific query about the video"
        ],
        markdown=True,
    )
    
    return video_agent

def analyze_video(video_url=None, video_path=None, query="Tell me about this video"):
    """
    Analyze a video using the video agent.
    
    Args:
        video_url (str, optional): URL of the video to analyze.
        video_path (str, optional): Path to the video file to analyze.
        query (str): Specific query about the video. Defaults to a general request.
        
    Returns:
        RunResponse: The response from the video agent.
    """
    try:
        agent = get_video_agent()
        videos = []
        
        if video_url:
            videos.append(Video(url=video_url))
        elif video_path:
            if isinstance(video_path, str):
                video_path = Path(video_path)
            videos.append(Video(filepath=video_path))
        else:
            raise ValueError("Either video_url or video_path must be provided")
            
        response = agent.run(
            query,
            videos=videos,
            stream=False
        )
        return response
    except Exception as e:
        print(f"Error analyzing video: {str(e)}")
        return f"Error analyzing video: {str(e)}"