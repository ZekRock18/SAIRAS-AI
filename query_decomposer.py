import json
import re
from agno.agent import Agent
from agno.models.groq import Groq
import os 
from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv('GROQ_API_KEY')

# Create a Query Decomposer agent that uses chain-of-thought reasoning.
decomposer = Agent(
    name="Query Decomposer",
    add_history_to_messages=True,
    num_history_responses=3,
    role="Analyze a user query using chain-of-thought reasoning and determine which specialized agents to use",
    model=Groq(id="qwen-2.5-32b"),
    instructions="""
    You are a query decomposer agent. Analyze the given query and determine which specialized agents are required.
    Your final answer must be a single valid JSON object that follows exactly this format:
    
    {"tasks": ["websearch", "financial", "research", "image", "geolocation", "video"]}
    
    Only include the agent types that apply to the query. Do not include any additional text, explanations, or chain-of-thought.
    Use the following rules:
    - If the query asks about current events, news, or general information, include "websearch".
    - If the query involves market data, stocks, or financial trends, include "financial".
    - If the query requires in-depth academic research, include "research".
    - If the query contains the special tag "@image:" followed by an image URL, include "image".
    - If the query asks about identifying a location from an image or contains the special tag "@geolocation:", include "geolocation".
    - If the query involves data visualization, plotting, or graphing, include "graph".
    - If the query contains the special tag "@video:" followed by a video URL, include "video".
    - If the query asks about analyzing or understanding a video, include "video".
    Now, analyze the following query and output only the JSON object as your final answer.
    """,
    markdown=False,
    show_tool_calls=False,
)

def extract_media_trigger(query: str) -> tuple:
    """
    Extract a media URL (image, video) and the actual query from the special trigger format.
    
    Args:
        query (str): The user query with potential media trigger
        
    Returns:
        tuple: (media_url, media_type, clean_query) - media URL if found, its type, and query without the trigger
    """
    # Look for @image:{URL}, @geolocation:{URL}, or @video:{URL} pattern
    image_pattern = r'@image:{([^}]+)}'
    geo_pattern = r'@geolocation:{([^}]+)}'
    video_pattern = r'@video:{([^}]+)}'
    
    image_match = re.search(image_pattern, query)
    geo_match = re.search(geo_pattern, query)
    video_match = re.search(video_pattern, query)
    
    if geo_match:
        media_url = geo_match.group(1).strip()
        # Remove the trigger from the query
        clean_query = re.sub(geo_pattern, '', query).strip()
        return media_url, "geolocation", clean_query
    elif image_match:
        media_url = image_match.group(1).strip()
        # Remove the trigger from the query
        clean_query = re.sub(image_pattern, '', query).strip()
        return media_url, "image", clean_query
    elif video_match:
        media_url = video_match.group(1).strip()
        # Remove the trigger from the query
        clean_query = re.sub(video_pattern, '', query).strip()
        return media_url, "video", clean_query
    
    return None, None, query

def decompose(query: str) -> dict:
    """
    Decomposes a query into tasks and extracts any media URL (image, video).
    
    Args:
        query (str): The user query
        
    Returns:
        dict: Contains 'tasks' (list of agent types), 'media_url' (if any), 'media_type', and 'clean_query'
    """
    # First extract any media trigger
    media_url, media_type, clean_query = extract_media_trigger(query)
    
    # Process the clean query with the decomposer
    run_response = decomposer.run(clean_query, stream=False)
    
    result = {
        "tasks": [],
        "media_url": media_url,
        "media_type": media_type,
        "clean_query": clean_query
    }
    
    try:
        # The RunResponse object has a 'content' attribute that likely contains our data
        if hasattr(run_response, 'content') and run_response.content:
            # This might already be parsed JSON data
            if isinstance(run_response.content, dict):
                result["tasks"] = run_response.content.get("tasks", [])
            else:
                # If it's a string, parse it
                data = json.loads(run_response.content)
                result["tasks"] = data.get("tasks", [])
        
        # Alternative: use the to_json() method
        elif hasattr(run_response, 'to_json'):
            data = json.loads(run_response.to_json())
            result["tasks"] = data.get("tasks", [])
        
        # If neither works, try get_content_as_string()
        elif hasattr(run_response, 'get_content_as_string'):
            content_str = run_response.get_content_as_string()
            data = json.loads(content_str)
            result["tasks"] = data.get("tasks", [])
            
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        print(f"Error extracting or parsing content: {e}")
        print(f"Response content type: {run_response.content_type if hasattr(run_response, 'content_type') else 'unknown'}")
        print(f"Response content: {run_response.content if hasattr(run_response, 'content') else 'unknown'}")
        
        # Fallback using simple keyword matching
        query_lower = clean_query.lower()
        tasks = []
        if any(kw in query_lower for kw in ["news", "latest", "event", "search"]):
            tasks.append("websearch")
        if any(kw in query_lower for kw in ["market", "financial", "stock", "price"]):
            tasks.append("financial")
        if any(kw in query_lower for kw in ["research", "study", "paper", "academic"]):
            tasks.append("research")
        if any(kw in query_lower for kw in ["location", "where is this", "identify place", "geolocation"]):
            tasks.append("geolocation")

        result["tasks"] = tasks
    
    # Force add appropriate task if media URL is detected
    if media_url:
        if media_type == "geolocation" and "geolocation" not in result["tasks"]:
            result["tasks"].append("geolocation")
        elif media_type == "image" and "image" not in result["tasks"]:
            result["tasks"].append("image")
        elif media_type == "video" and "video" not in result["tasks"]:
            result["tasks"].append("video")
    
    return result
