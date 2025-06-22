from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools

import os
from dotenv import load_dotenv

load_dotenv()

# Validate API keys
if not os.getenv("GROQ_API_KEY"):
    print("Warning: GROQ_API_KEY not found in environment")
    exit(1)

if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY not found in environment")

try:
    # Option 1: Use the most capable production model
    agent = Agent(
        model=Groq(id="llama-3.3-70b-versatile"),  # Updated to current model
        description="You are an assistant. Use the available tools to research and provide comprehensive answers to questions.",
        tools=[DuckDuckGoTools()],
        markdown=True,
        show_tool_calls=True,  # Show the tool calls
        max_loops=3,  # Allow multiple tool calls if needed
    )
    
    # Test with a valid question
    print("Testing with FIFA World Cup question...")
    response = agent.run("Who won the 2022 FIFA World Cup?")
    print("Final Answer:")
    print(response.content)
    
    print("\n" + "="*50 + "\n")
    
    # Test with another question
    print("Testing with current news...")
    response = agent.run("What are the latest developments in AI in 2025?")
    print("Final Answer:")
    print(response.content)
    
except Exception as e:
    print(f"Error with Groq model: {e}")
    
    # Fallback to OpenAI if Groq fails
    try:
        print("Trying OpenAI fallback...")
        agent_fallback = Agent(
            model=OpenAIChat(id="gpt-4o-mini"),
            description="You are an assistant please reply based on the question.",
            tools=[DuckDuckGoTools()],
            markdown=True
        )
        
        agent_fallback.print_response("Who won the 2022 FIFA World Cup?")
        
    except Exception as e2:
        print(f"Both models failed. Groq: {e}, OpenAI: {e2}")

# Alternative models you can try:
"""
Other Groq models to experiment with:

Production models (stable):
- Groq(id="llama-3.1-8b-instant")      # Faster, smaller model
- Groq(id="gemma2-9b-it")              # Google's Gemma model

Preview models (experimental):
- Groq(id="qwen-2.5-coder-32b")        # Better for coding tasks
- Groq(id="qwen-qwq-32b")              # Reasoning-focused
- Groq(id="deepseek-r1-distill-llama-70b")  # DeepSeek reasoning

Vision models (for image + text):
- Groq(id="llama-3.2-11b-vision-preview")
- Groq(id="llama-3.2-90b-vision-preview")
"""