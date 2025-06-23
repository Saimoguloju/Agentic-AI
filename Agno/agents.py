from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

import os
from dotenv import load_dotenv

load_dotenv()

# Validate OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not found in environment")
    print("Please set your OpenAI API key in the .env file or environment variables")
    exit(1)

try:
    # Create agent with OpenAI model
    agent = Agent(
        model=OpenAIChat(id="gpt-4o"),  # Use GPT-4o for best performance
        description="You are an intelligent assistant. Use the available tools to research and provide comprehensive answers to questions.",
        tools=[DuckDuckGoTools()],
        markdown=True,
        show_tool_calls=True,  # Show the tool calls for transparency
        # max_loops=3,  # REMOVED - this parameter is not supported
    )
    
    # Test with a factual question
    print("Testing with FIFA World Cup question...")
    response = agent.run("Who won the 2022 FIFA World Cup?")
    print("Final Answer:")
    print(response.content)
    
    print("\n" + "="*50 + "\n")
    
    # Test with current information
    print("Testing with current news...")
    response = agent.run("What are the latest developments in AI in 2025?")
    print("Final Answer:")
    print(response.content)
    
    print("\n" + "="*50 + "\n")
    
    # Test with a more complex research question
    print("Testing with complex research question...")
    response = agent.run("What are the key differences between GPT-4 and Claude 3, and which is better for coding tasks?")
    print("Final Answer:")
    print(response.content)
    
except Exception as e:
    print(f"Error running agent: {e}")
    print("Please check your API key and internet connection")

# Alternative OpenAI models you can try:
"""
OpenAI model options:

Production models:
- OpenAIChat(id="gpt-4o")              # Most capable, best for complex tasks
- OpenAIChat(id="gpt-4o-mini")         # Faster and cheaper, good for most tasks
- OpenAIChat(id="gpt-4-turbo")         # Previous generation, still very capable
- OpenAIChat(id="gpt-3.5-turbo")       # Fastest and cheapest, basic tasks

For coding specifically:
- OpenAIChat(id="gpt-4o")              # Best overall coding performance
- OpenAIChat(id="gpt-4o-mini")         # Good balance of speed and capability

For research tasks:
- OpenAIChat(id="gpt-4o")              # Best for complex research and analysis
"""

# If you need to control the number of iterations/loops, you might need to:
# 1. Check the agno documentation for the correct parameter name
# 2. Or implement your own loop control in the agent.run() calls
# 3. Or use a different agent configuration method