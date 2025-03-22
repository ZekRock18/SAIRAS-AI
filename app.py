from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
import asyncio
from orchestrator import decompose, get_agent_team
from automation_agent import run_search
import re


def clean_terminal_output(text):
    """Remove ANSI color codes and other terminal formatting characters from text"""
    # Remove ANSI escape sequences for colors
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    
    # Remove box drawing characters and other special unicode
    text = text.replace('─', '-')
    text = text.replace('│', '|')
    text = text.replace('┌', '+')
    text = text.replace('┐', '+')
    text = text.replace('└', '+')
    text = text.replace('┘', '+')
    text = text.replace('├', '+')
    text = text.replace('┤', '+')
    text = text.replace('┬', '+')
    text = text.replace('┴', '+')
    text = text.replace('┼', '+')
    
    return text

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Simple in-memory user database for demonstration
users = {}

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users and check_password_hash(users[email]['password'], password):
            session['user_id'] = email
            session['username'] = users[email]['name']
            # Store username in session for display in dashboard
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        
        if email in users:
            flash('Email already registered')
        elif password != confirm_password:
            flash('Passwords do not match')
        else:
            # Store user in our simple database
            users[email] = {
                'name': name,
                'password': generate_password_hash(password)
            }
            session['user_id'] = email
            session['username'] = name
            return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

# Agentic AI route
@app.route('/agentic-ai', methods=['GET', 'POST'])
def agentic_ai():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    response = None
    if request.method == 'POST':
        query = request.form.get('query')
        try:
            # Integrate with orchestrator.py
            decomposition_result = decompose(query)
            team_agent = get_agent_team(decomposition_result)
            
            # Get response from the agent team - using print_response instead of get_response
            # Create a StringIO object to capture the printed output
            import io
            from contextlib import redirect_stdout
            
            output = io.StringIO()
            with redirect_stdout(output):
                team_agent.print_response(decomposition_result.get('clean_query', query))
            
            # Get the captured output as the response
            response = output.getvalue()
            # Clean the response to remove terminal formatting
            response = clean_terminal_output(response)
        except Exception as e:
            response = f"Error processing query: {str(e)}"
    
    return render_template('dashboard.html', active_tab='agentic_ai', response=response)

# Web Automation route
@app.route('/web-automation', methods=['GET', 'POST'])
def web_automation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    response = None
    if request.method == 'POST':
        task = request.form.get('task')
        try:
            # Run the automation task asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create a future to run the task
            future = asyncio.ensure_future(run_search(task))
            
            # Run the future to completion
            result = loop.run_until_complete(future)
            loop.close()
            
            response = "Web automation task completed successfully."
            if result:
                response = clean_terminal_output(str(result))
        except Exception as e:
            response = f"Error processing automation task: {str(e)}"
    
    return render_template('dashboard.html', active_tab='web_automation', response=response)

if __name__ == '__main__':
    app.run(debug=True)