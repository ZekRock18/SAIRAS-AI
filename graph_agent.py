import os
from pathlib import Path
from typing import Optional, Dict, List, Any

from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json

# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"]=os.getenv('GROQ_API_KEY')

# Define the query for graph generation
graph_query = """
You are a data visualization expert. Your task is to analyze the provided tabular data and create appropriate visualizations based on:
- Data types (numerical, categorical, temporal)
- Relationships between variables
- Trends and patterns
- Distribution of values

Instructions:
1. Examine the data structure and content
2. Choose appropriate chart types based on the data
3. Create clear and informative visualizations
4. Add proper titles, labels, and legends
5. Format the data appropriately for visualization

Supported chart types:
- Line charts for time series or continuous relationships
- Bar charts for categorical comparisons
- Scatter plots for correlation analysis
- Pie charts for composition analysis
- Box plots for distribution analysis
"""

def get_graph_agent():
    """
    Returns a Graph Agent configured with Groq for data visualization tasks.
    """
    graph_agent = Agent(
        name="Graph Agent",
        role="Generate visualizations from tabular data",
        model=Groq(id="qwen-2.5-32b"),
        markdown=True,
        instructions="Create clear and informative visualizations from tabular data.",
    )
    return graph_agent

def create_visualization(data: Dict[str, Any], chart_type: str = None, title: str = None, image_format: str = 'png') -> Dict[str, str]:
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    save_path = os.path.join(static_dir, f'graph_{hash(str(data))}')
    """
    Create a visualization from the provided data.
    
    Args:
        data (Dict[str, Any]): The data to visualize
        chart_type (str, optional): The type of chart to create
        
    Returns:
        Optional[str]: HTML string of the generated plot
    """
    try:
        # Convert data to pandas DataFrame if it's not already
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise ValueError("Data must be a dictionary or pandas DataFrame")
            
        # Determine chart type if not specified
        if not chart_type:
            # Simple logic to guess chart type based on data structure
            if len(df.select_dtypes(include=['datetime64']).columns) > 0:
                chart_type = 'line'
            elif len(df.select_dtypes(include=['number']).columns) >= 2:
                chart_type = 'scatter'
            else:
                chart_type = 'bar'
        
        # Create visualization based on chart type
        if chart_type == 'line':
            fig = px.line(df)
        elif chart_type == 'bar':
            fig = px.bar(df)
        elif chart_type == 'scatter':
            fig = px.scatter(df)
        elif chart_type == 'pie':
            fig = px.pie(df)
        elif chart_type == 'box':
            fig = px.box(df)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
            
        # Update layout for better appearance
        fig.update_layout(
            title_x=0.5,
            margin=dict(t=50, l=50, r=50, b=50),
            template='plotly_white'
        )
        
        # Save the plot as image if save_path is provided
        if save_path:
            # Ensure the directory exists
            save_dir = os.path.dirname(save_path)
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                
            # Add file extension if not provided
            if not save_path.lower().endswith(('.' + image_format)):
                save_path = f"{save_path}.{image_format}"
                
            try:
                fig.write_image(save_path, format=image_format)
            except Exception as e:
                print(f"Warning: Failed to save image: {e}")
        
        # Save both HTML and image versions
        html_path = save_path + '.html'
        img_path = save_path + '.' + image_format
        
        try:
            fig.write_html(html_path)
            fig.write_image(img_path, format=image_format)
            
            # Return both paths and HTML content
            return {
                'html_path': html_path,
                'image_path': img_path,
                'html_content': fig.to_html(include_plotlyjs=True, full_html=False),
                'title': title or 'Graph Visualization'
            }
        except Exception as e:
            print(f"Error saving visualization: {e}")
            return None
        
    except Exception as e:
        raise RuntimeError(f"An error occurred while creating the visualization: {e}")