from flask import Flask, render_template, request, jsonify
import os
import asyncio
import json
from threading import Thread

# Import the orchestrator and automation agent
from orchestrator import decompose, get_agent_team, process_with_image_agent
from automation_agent import run_search

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/agentic-ai')
def agentic_ai():
    return render_template('agentic_ai.html')

@app.route('/web-automation')
def web_automation():
    return render_template('web_automation.html')

@app.route('/api/query', methods=['POST'])
def process_query():
    data = request.json
    query = data.get('query', '')
    
    if not query.strip():
        return jsonify({'error': 'Empty query'}), 400
    
    # Process the query using the orchestrator
    decomposition_result = decompose(query)
    
    # Handle image processing
    image_url = decomposition_result.get("image_url")
    clean_query = decomposition_result.get("clean_query", query)
    
    is_geolocation = "geolocation" in decomposition_result["tasks"]
    has_image_task = "image" in decomposition_result["tasks"] or is_geolocation
    
    response = {}
    
    if has_image_task and image_url:
        task_type = "geolocation" if is_geolocation else "image"
        
        # Process the image separately
        image_analysis = process_with_image_agent(image_url, clean_query, is_geolocation)
        
        # Check if there are other agent types
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
            
            # Get response from team agent
            agent_response = team_agent.run(enhanced_query)
            response = {
                'image_analysis': image_analysis,
                'agent_response': agent_response.content if hasattr(agent_response, 'content') else str(agent_response)
            }
        else:
            # Only image analysis is needed
            response = {'image_analysis': image_analysis}
    else:
        # Regular query without image
        team_agent = get_agent_team(decomposition_result)
        agent_response = team_agent.run(clean_query)
        response = {'agent_response': agent_response.content if hasattr(agent_response, 'content') else str(agent_response)}
    
    return jsonify(response)

@app.route('/api/automation', methods=['POST'])
def run_automation():
    data = request.json
    task = data.get('task', '')
    
    if not task.strip():
        return jsonify({'error': 'Empty task'}), 400
    
    # Run the automation task in a separate thread to not block the main thread
    def run_automation_task():
        asyncio.run(run_search(task))
    
    thread = Thread(target=run_automation_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'Automation task started', 'task': task})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True)