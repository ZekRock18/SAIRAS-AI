# SAiRAS

## 🚀 Overview

SAiRAS (Smart AI Responsive Agent System) is an advanced AI orchestration platform that intelligently routes user queries to specialized AI agents based on the query type. The system can handle text, images, and video inputs, providing comprehensive responses by leveraging the strengths of different AI models and tools.

This project demonstrates a modular approach to AI agent orchestration, where a central system decomposes queries and delegates tasks to specialized agents, then synthesizes their responses into a cohesive answer.

## ✨ Features

- **Query Decomposition**: Automatically analyzes user queries to determine which specialized agents are needed
- **Multi-Modal Support**: Handles text, image, and video inputs
- **Specialized Agents**:
  - **Web Search Agent**: Retrieves up-to-date information from the web
  - **Financial Agent**: Analyzes financial data, stocks, and market trends
  - **Research Agent**: Conducts in-depth academic research
  - **Image Agent**: Analyzes images and provides detailed descriptions
  - **Geolocation Agent**: Identifies locations from images
  - **Video Agent**: Analyzes video content
  - **Automation Agent**: Performs browser automation for complex web-based tasks
- **Team Collaboration**: Combines insights from multiple agents for comprehensive responses
- **Streaming Responses**: Provides real-time streaming of agent responses

## 🏗️ Architecture

The system follows a modular architecture with these key components:

1. **Query Decomposer**: Analyzes user input to determine which specialized agents are needed
2. **Orchestrator**: Manages the workflow between different agents and combines their responses
3. **Specialized Agents**: Individual AI agents with specific capabilities (web search, financial analysis, etc.)
4. **Team Agent**: Coordinates the work of multiple specialized agents and synthesizes their responses

## 🛠️ Installation

### Prerequisites

- Python 3.10 or higher
- Groq API key (for LLM access)
- Google API key (for Gemini model access)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ZekRock18/SAIRAS-AI.git
   cd SAIRAS-AI
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## 🚀 Usage

Run the orchestrator to start the system:

```bash
python orchestrator.py
```

### Query Examples

- **General Knowledge**: "What are the latest developments in quantum computing?"
- **Financial Analysis**: "How has Tesla stock performed over the last quarter?"
- **Research Question**: "Summarize recent research on climate change mitigation strategies"
- **Image Analysis**: `@image:{image_url} What can you tell me about this image?`
- **Geolocation**: `@geolocation:{image_url} Where was this photo taken?`
- **Video Analysis**: `@video:{video_url} Summarize what happens in this video`

### Special Commands

- `@image:{image_url} your prompt` - For general image analysis
- `@geolocation:{image_url}` - For identifying locations from images
- `@video:{video_url} your prompt` - For video analysis

## 🧠 Technical Implementation

### Agent Framework

The system uses the Agno framework to create and manage AI agents. Each agent is configured with:

- A specific LLM (Groq, Gemini)
- Specialized tools (DuckDuckGo search, financial data tools, etc.)
- Custom instructions tailored to its specific role
- Conversation history management

### Query Decomposition

The Query Decomposer uses chain-of-thought reasoning to analyze user queries and determine which specialized agents are required. It extracts special commands for media processing and cleans the query for further processing.

### Team Coordination

The Team Agent coordinates the work of multiple specialized agents, breaking down complex tasks into subtasks and assigning them to appropriate agents. It then integrates their responses into a cohesive answer.

### Automation Agent

The Automation Agent is a powerful component that enables browser automation for complex web-based tasks. It leverages:

- **Google's Gemini Model**: Uses the advanced gemini-2.0-flash-exp model for intelligent browser interaction
- **Browser Automation**: Utilizes the browser_use framework to navigate websites, fill forms, and extract information
- **Asynchronous Processing**: Implements asyncio for efficient task handling
- **Configurable Parameters**: Supports customizable viewport settings and action limits

This agent can be used independently or as part of the orchestrated system to handle tasks requiring web interaction, such as data collection, form submission, or complex web-based workflows.

For more detailed information about the Automation Agent, see [Automation Agent Documentation](docs/automation_agent_details.md).

## 📊 Future Enhancements

- Add support for audio processing
- Implement memory systems for persistent context across sessions
- Add more specialized agents for domains like healthcare, legal, etc.
- Improve the UI with a web interface
- Add support for more LLM providers

## 📝 License

[MIT License](LICENSE)

## 🙏 Acknowledgements

- [Agno Framework](https://github.com/agno-ai/agno)
- [Groq](https://groq.com/) for their powerful LLM API
- [Google Gemini](https://deepmind.google/technologies/gemini/) for multimodal capabilities