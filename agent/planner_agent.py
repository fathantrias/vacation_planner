"""
LangGraph agent configuration for the vacation planner.
Uses create_react_agent with Groq LLM and custom tools.
"""

import os
from pathlib import Path
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from agent.tools import VACATION_PLANNER_TOOLS


def load_system_prompt(prompt_file: str = "system_prompt.txt") -> str:
    """Load system prompt from file."""
    prompt_path = Path(__file__).parent / "prompts" / prompt_file
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_vacation_planner_agent(groq_api_key: str, model: str = "llama-3.3-70b-versatile"):
    """
    Create and configure the vacation planner agent.
    
    Args:
        groq_api_key: Groq API key for authentication
        model: Groq model to use (default: llama-3.3-70b-versatile)
        
    Returns:
        Tuple of (agent, system_prompt) ready for execution
    """
    # Initialize Groq LLM
    llm = ChatGroq(
        api_key=groq_api_key,
        model=model,
        temperature=0.7,
        max_tokens=4096
    )
    
    # Load system prompt
    system_prompt_text = load_system_prompt()
    
    # Create the ReAct agent with tools (no binding to avoid tool registration issues)
    agent = create_react_agent(
        llm,
        tools=VACATION_PLANNER_TOOLS
    )
    
    return agent, system_prompt_text


def invoke_agent(agent, user_message: str, chat_history: list = None):
    """
    Invoke the agent with a user message and optional chat history.
    
    Args:
        agent: The compiled agent graph
        user_message: User's input message
        chat_history: List of previous messages (optional)
        
    Returns:
        Agent's response
    """
    if chat_history is None:
        chat_history = []
    
    # Prepare messages
    messages = chat_history + [{"role": "user", "content": user_message}]
    
    # Invoke the agent
    response = agent.invoke({"messages": messages})
    
    return response
