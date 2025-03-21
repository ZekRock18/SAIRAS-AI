from web_search_agent import get_web_agent
from financial_agent import get_finance_agent
from research_agent import get_research_agent
from image_agent import get_image_agent, analyze_image as analyze_general_image
from geolocation_agent import get_geo_agent, analyze_image as analyze_geo_image
from video_agent import get_video_agent, analyze_video
from query_decomposer import decompose
from agno.agent import Agent
from agno.models.groq import Groq
from agno.media import Image, Video

import os 
from dotenv import load_dotenv
import json

load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv('GROQ_API_KEY')

def get_team_agents(decomposition_result):
    """
    Build a list of specialized agents based on the tasks from the Query Decomposer.
    
    Args:
        decomposition_result (dict): Contains 'tasks', 'image_url', and 'clean_query'
        
    Returns:
        list: List of specialized agents
    """
    team = []
    agent_types = decomposition_result["tasks"]
    
    if "websearch" in agent_types:  
        team.append(get_web_agent())
    if "financial" in agent_types:
        team.append(get_finance_agent())
    if "research" in agent_types:
        team.append(get_research_agent())
    if "geolocation" in agent_types and not decomposition_result.get("image_url"):
        # Only add to team if not handling image separately
        team.append(get_geo_agent())

    
    # Note: We handle the image agent separately, not as part of the team
    # to avoid message format issues with Groq
    
    return team

def process_with_image_agent(image_url, query, is_geolocation=False):
    """
    Process an image query separately using the image agent or geolocation agent.
    
    Args:
        image_url (str): URL of the image to analyze
        query (str): Query about the image
        is_geolocation (bool): Whether to use geolocation agent
        
    Returns:
        str: The image analysis result
    """
    print(f"Processing image: {image_url}")
    
    if is_geolocation:
        image_result = analyze_geo_image(image_url)
    else:
        image_result = analyze_general_image(image_url, query)
    
    # Extract the content from the response
    if hasattr(image_result, 'content'):
        return image_result.content
    elif hasattr(image_result, 'to_json'):
        data = json.loads(image_result.to_json())
        return data.get("content", "No image analysis available")
    elif hasattr(image_result, 'get_content_as_string'):
        return image_result.get_content_as_string()
    else:
        return "Could not process image analysis result"

def get_agent_team(decomposition_result):
    """
    Creates a team agent that aggregates the responses from the selected specialized agents.
    
    Args:
        decomposition_result (dict): Contains 'tasks', 'image_url', and 'clean_query'
        
    Returns:
        Agent: The team agent
    """
    # Create static directory for storing graphs if it doesn't exist
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    team_agents = get_team_agents(decomposition_result)
    if not team_agents:
        # Default to web search if no specific type is determined.
        team_agents = [get_web_agent()]
    
    team_agent = Agent(
        team=team_agents,
        model=Groq(id="deepseek-r1-distill-llama-70b"),  # Team leader model
        add_history_to_messages=True,
        num_history_responses=3,  
        instructions=[
            "Enhance the user prompt in a more detailed way and then use that prompt to answer the question.",
            "Breakdown your tasks into smaller subtasks step by step and assign each subtask to an agent. Also show the steps.",
            "Always include sources; format financial data as tables if applicable; provide a structured research report if needed.",
            "When multiple agents are used, integrate their responses into a cohesive answer.",
            "If you think we need more agents for a speific topic other than the ones we have, you can be that agent and research on that topic and then answer the question. Mention that you are an agent for the question asked",
        ],
        markdown=True,
        show_tool_calls=True,
        
    )
    return team_agent

def main():
    print("Agent Orchestrator (press Ctrl+C to exit)")
    print("-----------------------------------------")
    print("Special commands:")
    print("@image:{image_url} your prompt - For general image analysis")
    print("@geolocation:{image_url} - For identifying locations from images")
    print("-----------------------------------------")
    
    try:
        while True:
            query = input("\nEnter your query: ")
            if not query.strip():
                continue
                
            decomposition_result = decompose(query)
            print("Decomposition result:", decomposition_result["tasks"])
            
            # Handle image processing
            image_url = decomposition_result.get("image_url")
            clean_query = decomposition_result.get("clean_query", query)
            
            is_geolocation = "geolocation" in decomposition_result["tasks"]
            has_image_task = "image" in decomposition_result["tasks"] or is_geolocation
            
            if has_image_task and image_url:
                task_type = "geolocation" if is_geolocation else "image"
                print(f"{task_type.capitalize()} task detected with image: {image_url}")
                
                # First, process the image separately
                image_analysis = process_with_image_agent(image_url, clean_query, is_geolocation)
                
                # Then, if there are other agent types, process them separately
                other_tasks = [t for t in decomposition_result["tasks"] if t != "image" and t != "geolocation"]
                
                if other_tasks:
                    # Create a modified decomposition result without image task
                    modified_result = {
                        "tasks": other_tasks,
                        "clean_query": clean_query
                    }
                    
                    team_agent = get_agent_team(modified_result)
                    
                    # Add context from image analysis for other agents
                    enhanced_query = f"""
Based on {task_type} analysis which shows: 
{image_analysis[:300]}... 

Please address the following query:
{clean_query}
"""
                    
                    print("\nProcessing with team agent...")
                    team_agent.print_response(enhanced_query, stream=True)
                else:
                    # Only image analysis is needed
                    print(f"\n{task_type.capitalize()} Analysis Result:")
                    print(image_analysis)
            else:
                # Regular query without image
                team_agent = get_agent_team(decomposition_result)
                team_agent.print_response(clean_query, stream=True)
                
            print("\n-----------------------------------------")
    
    except KeyboardInterrupt:
        print("\nExiting the program. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Please try again.")

if __name__ == "__main__":
    main()