import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_community.llms import Ollama

from langchain_core.messages import (
    HumanMessage, 
    SystemMessage, 
    ToolMessage
)



# Load environment variables
load_dotenv()

llm = Ollama(
    model=os.getenv("OLLAMA_MODEL"),
    base_url=os.getenv("OLLAMA_BASE_URL"),
    temperature=0.4,
)

# Define tools
@tool("multiply")
def multiply(x: int, y: int) -> int:
  """Multiply two numbers together."""
  return x * y

@tool("add")
def add(x: int, y: int) -> int:
  """Add two numbers together."""
  return x + y

tools = [multiply, add]
tool_map = {tool.name: tool for tool in tools}

# Create tool definitions for the prompt
tool_definitions = "\n".join([
    f"- {tool.name}: {tool.description}" 
    for tool in tools
])

# System prompt that explains available tools
system_prompt = f"""You are a helpful assistant with access to the following tools:

{tool_definitions}

When you need to use a tool, respond with TOOL_USE: [tool_name(params=[params])]
Then provide the result in your response."""

messages = [
  SystemMessage(content=system_prompt),
  HumanMessage(content="What is 3 multiplied by 2?")
]

response = llm.invoke(messages)
print("LLM Response:")
print(response)

# For OpenAI/Claude models that support bind_tools(), you would do:
# llm_with_tools = llm.bind_tools(tools)
# response = llm_with_tools.invoke(messages)
# 
# But Ollama requires manual tool invocation through prompts