"""
Example: Using Ollama with LangChain and LangGraph

This module demonstrates how to set up and use a local Ollama LLM
with LangChain for basic chat and LangGraph for agentic workflows.
"""

import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")


def example_1_basic_chat():
    """Example 1: Basic chat with Ollama LLM"""
    print("\n" + "="*60)
    print("Example 1: Basic Chat with Ollama")
    print("="*60)
    
    llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
    
    response = llm.invoke("What is LangChain? Explain briefly.")
    print(f"\nQuery: What is LangChain?")
    print(f"Response:\n{response}")


def example_2_prompt_template():
    """Example 2: Using prompt templates with Ollama"""
    print("\n" + "="*60)
    print("Example 2: Prompt Template with Ollama")
    print("="*60)
    
    llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_template(
        """You are a helpful Python programming assistant.
        Answer the following question concisely.
        
        Question: {question}
        Answer:"""
    )
    
    # Chain the prompt with the LLM
    chain = prompt | llm
    
    response = chain.invoke({"question": "How do you read a file in Python?"})
    print(f"\nQuestion: How do you read a file in Python?")
    print(f"Response:\n{response}")


def example_3_conversation():
    """Example 3: Multi-turn conversation"""
    print("\n" + "="*60)
    print("Example 3: Multi-turn Conversation")
    print("="*60)
    
    llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
    
    # Simulate a conversation
    messages = [
        "What are the main benefits of using Python?",
        "Can you give me an example of a Python decorator?",
        "How do decorators help with code organization?",
    ]
    
    for msg in messages:
        print(f"\nUser: {msg}")
        response = llm.invoke(msg)
        print(f"Assistant: {response[:200]}...")  # Print first 200 chars


def example_4_streaming():
    """Example 4: Streaming responses (if supported)"""
    print("\n" + "="*60)
    print("Example 4: Streaming Response")
    print("="*60)
    
    llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
    
    print("\nQuery: Tell me a short story about a robot learning to code")
    print("Response (streaming):\n")
    
    # Stream the response
    for chunk in llm.stream("Tell me a short story about a robot learning to code"):
        print(chunk, end="", flush=True)
    print("\n")


def example_5_langgraph_simple():
    """Example 5: Simple LangGraph workflow with Ollama
    
    This demonstrates a basic sequential workflow:
    1. Generate an idea
    2. Create a plan
    3. Generate implementation steps
    """
    print("\n" + "="*60)
    print("Example 5: LangGraph Simple Workflow")
    print("="*60)
    
    try:
        from langgraph.graph import StateGraph
        from typing import TypedDict
        
        class WorkflowState(TypedDict):
            topic: str
            idea: str
            plan: str
            steps: str
        
        llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        
        # Define workflow nodes
        def generate_idea(state):
            prompt = f"Generate a creative AI application idea about: {state['topic']}"
            state['idea'] = llm.invoke(prompt)
            return state
        
        def create_plan(state):
            prompt = f"Create a high-level plan for this idea: {state['idea'][:100]}..."
            state['plan'] = llm.invoke(prompt)
            return state
        
        def generate_steps(state):
            prompt = f"Generate implementation steps for: {state['plan'][:100]}..."
            state['steps'] = llm.invoke(prompt)
            return state
        
        # Build the graph
        graph = StateGraph(WorkflowState)
        graph.add_node("generate_idea", generate_idea)
        graph.add_node("create_plan", create_plan)
        graph.add_node("generate_steps", generate_steps)
        
        # Connect nodes sequentially
        graph.add_edge("generate_idea", "create_plan")
        graph.add_edge("create_plan", "generate_steps")
        
        graph.set_entry_point("generate_idea")
        graph.set_finish_point("generate_steps")
        
        # Run the workflow
        app = graph.compile()
        initial_state = {"topic": "healthcare AI", "idea": "", "plan": "", "steps": ""}
        
        print("\nRunning workflow for topic: healthcare AI")
        result = app.invoke(initial_state)
        
        print(f"\nIdea: {result['idea'][:200]}...")
        print(f"\nPlan: {result['plan'][:200]}...")
        print(f"\nImplementation Steps: {result['steps'][:200]}...")
        
    except ImportError:
        print("LangGraph not installed. Install with: uv pip install langgraph")


def main():
    """Run all examples"""
    print("\n🤖 LangChain + LangGraph + Ollama Examples")
    print(f"Using Ollama model: {OLLAMA_MODEL}")
    print(f"Base URL: {OLLAMA_BASE_URL}")
    
    # Check Ollama connection
    try:
        import requests
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            print("✓ Ollama is running")
        else:
            print("✗ Ollama connection issue")
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("  Make sure Ollama is running: ollama serve")
        return
    
    # Run examples
    try:
        example_1_basic_chat()
        example_2_prompt_template()
        example_3_conversation()
        # Uncomment to enable streaming (slower)
        # example_4_streaming()
        example_5_langgraph_simple()
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
