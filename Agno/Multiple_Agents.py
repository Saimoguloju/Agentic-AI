from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
import os
from dotenv import load_dotenv

load_dotenv()

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Validate OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not found in environment")
    print("Please set your OpenAI API key in the .env file or environment variables")
    exit(1)

# Web search agent using OpenAI
web_agent = Agent(
    name="Web Agent",
    role="search the web for information",
    model=OpenAIChat(id="gpt-4o-mini"),   
    tools=[DuckDuckGoTools()],
    instructions="Always include the sources",
    show_tool_calls=True,
    markdown=True,
)

# Finance agent using OpenAI
finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    model=OpenAIChat(id="gpt-4o"),   
    tools=[YFinanceTools(
        stock_price=True, 
        analyst_recommendations=True,
        stock_fundamentals=True,
        company_info=True
    )],
    instructions="Use tables to display data",
    show_tool_calls=True,
    markdown=True,
)

# Agent team coordinator using OpenAI
agent_team = Agent(
    team=[web_agent, finance_agent],
    model=OpenAIChat(id="gpt-4o"),  
    instructions=["Always include sources", "Use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)

# Run the analysis
agent_team.print_response("Analyze companies like Tesla, NVDA, Apple and suggest which to buy for long term")