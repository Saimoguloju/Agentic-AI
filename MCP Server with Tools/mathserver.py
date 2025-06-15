#!/usr/bin/env python3
"""
MCP Math Server - A simple MCP server that provides basic math operations.
This server runs via stdio transport and provides mathematical tools.
"""

import asyncio
import logging
import math
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.types as types

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("math-server")

# Create a MCP server
server = Server("math-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available mathematical tools.
    """
    return [
        Tool(
            name="add",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="subtract",
            description="Subtract second number from first number",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number (minuend)"},
                    "b": {"type": "number", "description": "Second number (subtrahend)"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="multiply",
            description="Multiply two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="divide",
            description="Divide first number by second number",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Dividend"},
                    "b": {"type": "number", "description": "Divisor (cannot be zero)"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="power",
            description="Raise a number to a power",
            inputSchema={
                "type": "object",
                "properties": {
                    "base": {"type": "number", "description": "Base number"},
                    "exponent": {"type": "number", "description": "Exponent"},
                },
                "required": ["base", "exponent"],
            },
        ),
        Tool(
            name="sqrt",
            description="Calculate square root of a number",
            inputSchema={
                "type": "object",
                "properties": {
                    "number": {
                        "type": "number", 
                        "description": "Number to find square root of",
                        "minimum": 0
                    },
                },
                "required": ["number"],
            },
        ),
        Tool(
            name="factorial",
            description="Calculate factorial of a non-negative integer",
            inputSchema={
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Non-negative integer",
                        "minimum": 0
                    },
                },
                "required": ["n"],
            },
        ),
        Tool(
            name="log",
            description="Calculate natural logarithm of a positive number",
            inputSchema={
                "type": "object",
                "properties": {
                    "number": {
                        "type": "number",
                        "description": "Positive number",
                        "minimum": 0,
                        "exclusiveMinimum": True
                    },
                },
                "required": ["number"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """
    Handle tool execution for mathematical operations.
    """
    try:
        if name == "add":
            result = arguments["a"] + arguments["b"]
            return [types.TextContent(
                type="text", 
                text=f"{arguments['a']} + {arguments['b']} = {result}"
            )]
            
        elif name == "subtract":
            result = arguments["a"] - arguments["b"]
            return [types.TextContent(
                type="text", 
                text=f"{arguments['a']} - {arguments['b']} = {result}"
            )]
            
        elif name == "multiply":
            result = arguments["a"] * arguments["b"]
            return [types.TextContent(
                type="text", 
                text=f"{arguments['a']} × {arguments['b']} = {result}"
            )]
            
        elif name == "divide":
            if arguments["b"] == 0:
                return [types.TextContent(
                    type="text", 
                    text="Error: Division by zero is undefined"
                )]
            result = arguments["a"] / arguments["b"]
            return [types.TextContent(
                type="text", 
                text=f"{arguments['a']} ÷ {arguments['b']} = {result}"
            )]
            
        elif name == "power":
            result = arguments["base"] ** arguments["exponent"]
            return [types.TextContent(
                type="text", 
                text=f"{arguments['base']}^{arguments['exponent']} = {result}"
            )]
            
        elif name == "sqrt":
            if arguments["number"] < 0:
                return [types.TextContent(
                    type="text", 
                    text="Error: Cannot calculate square root of negative number"
                )]
            result = math.sqrt(arguments["number"])
            return [types.TextContent(
                type="text", 
                text=f"√{arguments['number']} = {result}"
            )]
            
        elif name == "factorial":
            n = arguments["n"]
            if n < 0:
                return [types.TextContent(
                    type="text", 
                    text="Error: Factorial is not defined for negative numbers"
                )]
            result = math.factorial(n)
            return [types.TextContent(
                type="text", 
                text=f"{n}! = {result}"
            )]
            
        elif name == "log":
            if arguments["number"] <= 0:
                return [types.TextContent(
                    type="text", 
                    text="Error: Logarithm is only defined for positive numbers"
                )]
            result = math.log(arguments["number"])
            return [types.TextContent(
                type="text", 
                text=f"ln({arguments['number']}) = {result}"
            )]
            
        else:
            return [types.TextContent(
                type="text", 
                text=f"Error: Unknown tool '{name}'"
            )]
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [types.TextContent(
            type="text", 
            text=f"Error executing {name}: {str(e)}"
        )]

async def main():
    """
    Main function to run the math server using stdio transport.
    """
    try:
        logger.info("Starting MCP Math Server...")
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream, 
                write_stream, 
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())