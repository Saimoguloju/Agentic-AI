#!/usr/bin/env python3
"""
MCP Weather Server - A simple HTTP-based MCP server that provides weather information.
This server runs on http://localhost:8000/mcp and provides weather tools.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict
from aiohttp import web, web_request
from aiohttp.web_response import Response

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
import mcp.types as types

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-server")

# Create MCP server
server = Server("weather-server")

# Mock weather data for different cities
WEATHER_DATA = {
    "california": {
        "location": "California, USA",
        "temperature": 72,
        "unit": "°F",
        "condition": "Sunny",
        "humidity": 45,
        "wind_speed": 8,
        "wind_direction": "NW",
        "description": "Clear skies with gentle breeze"
    },
    "new york": {
        "location": "New York, USA", 
        "temperature": 68,
        "unit": "°F",
        "condition": "Partly Cloudy",
        "humidity": 60,
        "wind_speed": 12,
        "wind_direction": "E",
        "description": "Partly cloudy with moderate winds"
    },
    "london": {
        "location": "London, UK",
        "temperature": 15,
        "unit": "°C", 
        "condition": "Rainy",
        "humidity": 85,
        "wind_speed": 15,
        "wind_direction": "SW",
        "description": "Light rain with overcast skies"
    },
    "tokyo": {
        "location": "Tokyo, Japan",
        "temperature": 22,
        "unit": "°C",
        "condition": "Cloudy",
        "humidity": 70,
        "wind_speed": 10,
        "wind_direction": "N",
        "description": "Overcast with mild temperatures"
    },
    "sydney": {
        "location": "Sydney, Australia",
        "temperature": 25,
        "unit": "°C",
        "condition": "Sunny",
        "humidity": 55,
        "wind_speed": 14,
        "wind_direction": "SE",
        "description": "Beautiful sunny day with sea breeze"
    }
}

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available weather tools.
    """
    return [
        Tool(
            name="get_weather",
            description="Get current weather information for a specified location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or location name (e.g., 'California', 'New York', 'London')"
                    },
                },
                "required": ["location"],
            },
        ),
        Tool(
            name="get_forecast",
            description="Get weather forecast for a location (mock 3-day forecast)",
            inputSchema={
                "type": "object", 
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or location name"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days for forecast (1-7)",
                        "minimum": 1,
                        "maximum": 7,
                        "default": 3
                    }
                },
                "required": ["location"],
            },
        ),
        Tool(
            name="list_locations",
            description="List all available locations for weather data",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """
    Handle tool execution for weather operations.
    """
    try:
        if name == "get_weather":
            location = arguments["location"].lower().strip()
            
            # Find matching location
            weather_info = None
            for key, data in WEATHER_DATA.items():
                if key in location or location in key:
                    weather_info = data
                    break
            
            if weather_info:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                weather_report = f"""🌤️ Weather Report for {weather_info['location']}
📅 Current Time: {current_time}
🌡️ Temperature: {weather_info['temperature']}{weather_info['unit']}
☁️ Condition: {weather_info['condition']}
💧 Humidity: {weather_info['humidity']}%
💨 Wind: {weather_info['wind_speed']} mph {weather_info['wind_direction']}
📝 Description: {weather_info['description']}"""
                
                return [types.TextContent(type="text", text=weather_report)]
            else:
                available_locations = ", ".join(WEATHER_DATA.keys())
                return [types.TextContent(
                    type="text", 
                    text=f"❌ Weather data not available for '{arguments['location']}'. Available locations: {available_locations}"
                )]
                
        elif name == "get_forecast":
            location = arguments["location"].lower().strip()
            days = arguments.get("days", 3)
            
            # Find matching location
            base_weather = None
            for key, data in WEATHER_DATA.items():
                if key in location or location in key:
                    base_weather = data
                    break
            
            if base_weather:
                forecast_report = f"📊 {days}-Day Weather Forecast for {base_weather['location']}\n\n"
                
                for day in range(days):
                    # Create mock forecast data with slight variations
                    temp_variation = [-3, -1, 2, 4, -2, 1, 0][day % 7]
                    conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Clear"][day % 5]
                    
                    day_name = ["Today", "Tomorrow", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"][day]
                    temp = base_weather['temperature'] + temp_variation
                    
                    forecast_report += f"📅 {day_name}: {temp}{base_weather['unit']}, {conditions}\n"
                
                return [types.TextContent(type="text", text=forecast_report)]
            else:
                available_locations = ", ".join(WEATHER_DATA.keys())
                return [types.TextContent(
                    type="text", 
                    text=f"❌ Weather data not available for '{arguments['location']}'. Available locations: {available_locations}"
                )]
                
        elif name == "list_locations":
            locations_list = "🌍 Available Weather Locations:\n\n"
            for key, data in WEATHER_DATA.items():
                locations_list += f"• {data['location']} - {data['temperature']}{data['unit']}, {data['condition']}\n"
            
            return [types.TextContent(type="text", text=locations_list)]
            
        else:
            return [types.TextContent(
                type="text", 
                text=f"❌ Unknown tool: {name}"
            )]
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [types.TextContent(
            type="text", 
            text=f"❌ Error executing {name}: {str(e)}"
        )]

async def handle_sse(request: web_request.Request) -> Response:
    """
    Handle Server-Sent Events for MCP communication.
    """
    logger.info("SSE connection established")
    
    transport = SseServerTransport("/mcp", request)
    
    async with transport.connect() as streams:
        read_stream, write_stream = streams
        await server.run(read_stream, write_stream, server.create_initialization_options())
    
    return transport.response

async def handle_health(request: web_request.Request) -> web.Response:
    """
    Health check endpoint.
    """
    return web.json_response({
        "status": "healthy",
        "server": "weather-mcp-server",
        "timestamp": datetime.now().isoformat()
    })

def create_app() -> web.Application:
    """
    Create and configure the web application.
    """
    app = web.Application()
    
    # Add routes
    app.router.add_get("/mcp", handle_sse)
    app.router.add_post("/mcp", handle_sse)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/", handle_health)  # Root endpoint for basic check
    
    return app

async def main():
    """
    Main function to run the weather server.
    """
    try:
        logger.info("Starting MCP Weather Server on http://localhost:8000")
        
        app = create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, "localhost", 8000)
        await site.start()
        
        logger.info("🌤️ Weather Server is running!")
        logger.info("📡 MCP endpoint: http://localhost:8000/mcp")
        logger.info("❤️ Health check: http://localhost:8000/health")
        logger.info("Press Ctrl+C to stop the server")
        
        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Shutting down weather server...")
        finally:
            await runner.cleanup()
            
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())