# Google Agent Development Kit (ADK) - Complete Reference Guide

**Last Updated**: November 8, 2025  
**Version**: Python ADK v1.8.0+

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Core Concepts](#core-concepts)
4. [Agent Classes](#agent-classes)
5. [Tools & Integrations](#tools--integrations)
6. [Session Management](#session-management)
7. [Memory & Artifacts](#memory--artifacts)
8. [Evaluation & Testing](#evaluation--testing)
9. [Deployment](#deployment)
10. [CLI Commands](#cli-commands)
11. [Advanced Patterns](#advanced-patterns)
    - [Context Caching](#context-caching)
    - [Debugging with run_debug()](#debugging-with-run_debug)
    - [Tool Callbacks](#tool-callbacks)
    - [Model Callbacks](#model-callbacks)
    - [Plugins for Context Management](#plugins-for-context-management)
    - [FastMCP Integration](#fastmcp-integration)
    - [LiteLLM Context Caching](#litellm-context-caching)
    - [Asynchronous Tools for Parallelism](#asynchronous-tools-for-parallelism)
12. [Model Context Protocol (MCP) Integration](#model-context-protocol-mcp-integration)
13. [Multi-Agent Patterns](#multi-agent-patterns)
14. [Agent-to-Agent Communication](#agent-to-agent-communication)
15. [Project Structure](#project-structure)
16. [Configuration](#configuration)
17. [Best Practices](#best-practices)

---

## Overview

The Google Agent Development Kit (ADK) is an open-source, code-first Python toolkit for building, evaluating, and deploying sophisticated AI agents. It provides:

- **Flexible orchestration** for single and multi-agent systems
- **Rich tool ecosystem** with built-in integrations
- **Production-ready deployment** to Google Cloud
- **Evaluation framework** for testing agent performance
- **Support for various models** including Gemini, Ollama, and others via LiteLLM

---

## Installation

### Standard Installation

```bash
# Install stable release
pip install google-adk

# Install development version
pip install git+https://github.com/google/adk-python.git@main
```

### Development Setup

```bash
# Create virtual environment with uv
uv venv --python "python3.11" ".venv"
source .venv/bin/activate

# Install all dependencies
uv sync --all-extras

# Minimal testing setup
uv sync --extra test --extra eval --extra a2a
```

### Environment Setup

```bash
# For Gemini Developer API
export GEMINI_API_KEY='your-api-key'

# For Vertex AI
export GOOGLE_GENAI_USE_VERTEXAI=True
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='us-central1'
```

---

## Core Concepts

### 1. Agent

The fundamental building block representing an AI agent with a model, instructions, and tools.

```python
from google.adk import Agent
from google.adk.tools import google_search

agent = Agent(
    name="assistant",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    description="An assistant that can search the web.",
    tools=[google_search]
)
```

### 2. Runner

Manages agent execution, session handling, and event streaming.

```python
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

runner = Runner(
    app_name="my_app",
    agent=agent,
    session_service=InMemorySessionService()
)

# Run agent asynchronously
async def run_query():
    content = types.Content(
        role='user', 
        parts=[types.Part(text="What's the weather in Tokyo?")]
    )
    async for event in runner.run_async(
        user_id="user123",
        session_id="session456",
        new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"[{event.author}]: {part.text}")
```

### 3. App

A container for agents with plugins, resumability, and advanced configuration.

```python
from google.adk.apps import App, ResumabilityConfig
from google.adk.plugins import ContextFilterPlugin

app = App(
    name="my_app",
    root_agent=agent,
    plugins=[
        ContextFilterPlugin(num_invocations_to_keep=3)
    ],
    resumability_config=ResumabilityConfig(is_resumable=True)
)
```

---

## Agent Classes

### LlmAgent (Base Agent)

Standard agent powered by an LLM with support for tools and sub-agents.

```python
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

agent = LlmAgent(
    name="search_assistant",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    description="An assistant that can search the web.",
    tools=[google_search]
)
```

### Multi-Agent Coordinator

Hierarchical agent system with specialized sub-agents.

```python
from google.adk.agents import LlmAgent

# Define specialized agents
greeter = LlmAgent(
    name="greeter",
    model="gemini-2.5-flash",
    description="Greets users and provides welcoming messages.",
    instruction="You greet users warmly and professionally."
)

task_executor = LlmAgent(
    name="task_executor",
    model="gemini-2.5-flash",
    description="Executes tasks and provides solutions.",
    instruction="You execute tasks efficiently.",
    tools=[google_search]
)

# Create coordinator with sub-agents
coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.5-flash",
    description="Coordinates greetings and task execution.",
    instruction="Delegate tasks to appropriate sub-agents.",
    sub_agents=[greeter, task_executor]
)
```

### SequentialAgent

Agents that execute in a specific order.

```python
from google.adk.agents import SequentialAgent, LlmAgent

# Define agents for each step
research_agent = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="Research the topic thoroughly.",
    tools=[google_search]
)

writer_agent = LlmAgent(
    name="writer",
    model="gemini-2.5-flash",
    instruction="Write a comprehensive article based on the research."
)

editor_agent = LlmAgent(
    name="editor",
    model="gemini-2.5-flash",
    instruction="Edit and polish the article for publication."
)

# Create sequential workflow
content_pipeline = SequentialAgent(
    name="content_pipeline",
    description="Research, write, and edit content sequentially.",
    sub_agents=[research_agent, writer_agent, editor_agent]
)
```

### ParallelAgent

Agents that execute simultaneously for diverse perspectives.

```python
from google.adk.agents import ParallelAgent, LlmAgent

fact_checker = LlmAgent(
    name="fact_checker",
    model="gemini-2.5-flash",
    instruction="Verify facts in the content.",
    tools=[google_search]
)

sentiment_analyzer = LlmAgent(
    name="sentiment_analyzer",
    model="gemini-2.5-flash",
    instruction="Analyze sentiment of the content."
)

seo_optimizer = LlmAgent(
    name="seo_optimizer",
    model="gemini-2.5-flash",
    instruction="Suggest SEO improvements."
)

# Run multiple agents in parallel
parallel_analyzer = ParallelAgent(
    name="content_analyzer",
    description="Analyze content from multiple perspectives.",
    sub_agents=[fact_checker, sentiment_analyzer, seo_optimizer]
)
```

### LoopAgent

Iterative problem-solving agent with loop control.

```python
from google.adk.agents import LoopAgent, LlmAgent
from google.adk.tools import exit_loop

problem_solver = LlmAgent(
    name="problem_solver",
    model="gemini-2.5-flash",
    instruction="""Solve the problem step by step.
    Call exit_loop when you have a complete solution.""",
    tools=[exit_loop]
)

# Create loop agent with max iterations
iterative_solver = LoopAgent(
    name="iterative_solver",
    description="Solve problems through iterative refinement.",
    sub_agents=[problem_solver],
    max_iterations=5
)
```

---

## Tools & Integrations

### Built-in Tools

```python
from google.adk import Agent
from google.adk.tools import (
    google_search,      # Web search capability
    url_context,        # Extract content from URLs
    exit_loop          # Exit loop agents
)

agent = Agent(
    name="web_researcher",
    model="gemini-2.5-flash",
    instruction="Research topics using web search.",
    tools=[google_search, url_context]
)
```

### Custom Function Tools

```python
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
import random

def roll_die(sides: int, tool_context: ToolContext) -> int:
    """Roll a die and return the result.

    Args:
        sides: The integer number of sides the die has.

    Returns:
        An integer of the result of rolling the die.
    """
    result = random.randint(1, sides)
    if 'rolls' not in tool_context.state:
        tool_context.state['rolls'] = []
    tool_context.state['rolls'].append(result)
    return result

async def check_prime(nums: list[int]) -> str:
    """Check if given numbers are prime.

    Args:
        nums: The list of numbers to check.

    Returns:
        A string indicating which numbers are prime.
    """
    primes = {
        num for num in nums 
        if num > 1 and all(num % i != 0 for i in range(2, int(num**0.5) + 1))
    }
    return f"{', '.join(str(n) for n in primes)} are prime numbers." \
        if primes else "No prime numbers found."

dice_agent = Agent(
    model='gemini-2.5-flash',
    name='dice_agent',
    description='Agent that can roll dice and check prime numbers.',
    instruction="""You roll dice and check prime numbers.
    Always call roll_die first, then check_prime with the results.""",
    tools=[roll_die, check_prime]
)
```

### BigQuery Toolset

```python
from google.adk import Agent
from google.adk.tools.bigquery_toolset import BigQueryToolset

# Initialize BigQuery toolset
bigquery_tools = BigQueryToolset(project_id="my-project")

# Create agent with BigQuery tools
data_analyst = Agent(
    name="data_analyst",
    model="gemini-2.5-flash",
    instruction="Analyze data using BigQuery.",
    tools=bigquery_tools.get_tools()
)
```

### REST API Tools with OAuth2

```python
from google.adk import Agent
from google.adk.auth import AuthConfig, OAuth2AuthScheme
from google.adk.tools import RestAPITool

# Define OAuth2 configuration
oauth_config = OAuth2AuthScheme(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authorization_url="https://provider.com/oauth/authorize",
    token_url="https://provider.com/oauth/token",
    scopes=["read", "write"]
)

# Create REST API tool with authentication
api_tool = RestAPITool(
    name="secure_api",
    openapi_spec_url="https://api.example.com/openapi.json",
    auth_config=AuthConfig(scheme=oauth_config)
)

secure_agent = Agent(
    name="secure_agent",
    model="gemini-2.5-flash",
    instruction="Use the secure API to access protected resources.",
    tools=[api_tool]
)
```

### Human-in-the-Loop Tools

```python
from google.adk import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_configs import ToolConfig, ConfirmationConfig

def delete_file(path: str) -> str:
    """Delete a file from the system."""
    import os
    os.remove(path)
    return f"Deleted {path}"

# Create tool with confirmation required
delete_tool = FunctionTool(
    func=delete_file,
    config=ToolConfig(
        confirmation=ConfirmationConfig(
            require_confirmation=True,
            confirmation_prompt="Are you sure you want to delete this file?"
        )
    )
)

safe_agent = Agent(
    name="safe_agent",
    model="gemini-2.5-flash",
    instruction="Help manage files safely.",
    tools=[delete_tool]
)
```

### Code Execution

```python
from google.adk import Agent
from google.adk.code_executors import (
    BuiltInCodeExecutor,
    AgentEngineSandboxCodeExecutor
)

# Built-in code executor
code_agent = Agent(
    name="code_executor",
    model="gemini-2.5-flash",
    instruction="Execute Python code to solve problems.",
    code_executor=BuiltInCodeExecutor()
)

# Secure sandboxed executor
sandbox_agent = Agent(
    name="sandbox_executor",
    model="gemini-2.5-flash",
    instruction="Execute code safely in a sandboxed environment.",
    code_executor=AgentEngineSandboxCodeExecutor()
)
```

### Long-Running Tasks

```python
from google.adk.apps import App, ResumabilityConfig
from google.adk import Agent
from google.adk.tools import LongRunningFunctionTool

async def long_computation(data: str) -> str:
    """Perform a long-running computation."""
    import asyncio
    await asyncio.sleep(300)  # Simulates 5-minute task
    return f"Processed: {data}"

# Create long-running tool
compute_tool = LongRunningFunctionTool(func=long_computation)

agent = Agent(
    name="compute_agent",
    model="gemini-2.5-flash",
    instruction="Execute long computations.",
    tools=[compute_tool]
)

# Enable resumability
app = App(
    name="resumable_app",
    root_agent=agent,
    resumability_config=ResumabilityConfig(is_resumable=True)
)
```

---

## Session Management

### InMemorySessionService

```python
from google.adk.sessions import InMemorySessionService, Session

session_service = InMemorySessionService()

async def session_management_example():
    # Create session with initial state
    session = await session_service.create_session(
        app_name="my_app",
        user_id="user123",
        state={
            "preferences": {"language": "en"}, 
            "context": "customer_support"
        }
    )

    # Retrieve existing session
    retrieved = await session_service.get_session(
        app_name="my_app",
        user_id="user123",
        session_id=session.id
    )

    # Update session state
    await session_service.update_session_state(
        app_name="my_app",
        user_id="user123",
        session_id=session.id,
        state={"preferences": {"language": "es"}}
    )

    # List all sessions for user
    sessions = await session_service.list_sessions(
        app_name="my_app",
        user_id="user123"
    )

    return session
```

### Session Rewinding

```python
from google.adk import Runner

async def rewind_session():
    # Rewind session to before a specific invocation
    await runner.rewind_session(
        user_id="user123",
        session_id="session456",
        invocation_id="invocation789"
    )
```

### Custom Session Service

```python
from google.adk.cli.service_registry import ServiceRegistry
from google.adk.sessions import BaseSessionService

class MyCustomSessionService(BaseSessionService):
    # Implement custom session management logic
    pass

# Register custom service
ServiceRegistry.register_session_service(MyCustomSessionService)
```

---

## Memory & Artifacts

### Memory Service

```python
from google.adk.memory import InMemoryMemoryService

memory_service = InMemoryMemoryService()
```

### Artifact Service

```python
from google.adk.artifacts import InMemoryArtifactService

artifact_service = InMemoryArtifactService()
```

### Full Configuration with Services

```python
from google.adk.apps import App, ResumabilityConfig
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService

# Define root agent
root_agent = Agent(
    name="assistant",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant."
)

# Create app with resumability
app = App(
    name="my_application",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True)
)

# Initialize all services
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
memory_service = InMemoryMemoryService()

# Create runner with full configuration
runner = Runner(
    app=app,
    session_service=session_service,
    artifact_service=artifact_service,
    memory_service=memory_service
)

# Run with session management
async def run_with_session():
    session = await session_service.create_session(
        app_name="my_application",
        user_id="user123",
        state={"context": "initial_state"}
    )

    from google.genai import types
    message = types.Content(
        role='user', 
        parts=[types.Part(text="Hello!")]
    )

    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=message
    ):
        if event.content:
            print(event.content)
```

---

## Evaluation & Testing

### Define Evaluation Cases

```python
from google.adk.evaluation import EvalCase
from google.genai import types

eval_cases = [
    EvalCase(
        query=types.Content(
            role='user', 
            parts=[types.Part(text="What is 2+2?")]
        ),
        expected_response="4",
        expected_tool_calls=[]
    ),
    EvalCase(
        query=types.Content(
            role='user', 
            parts=[types.Part(text="Search for Python tutorials")]
        ),
        expected_tool_calls=["google_search"]
    )
]
```

### Programmatic Evaluation

```python
from google.adk import Agent
from google.adk.evaluation import Evaluator
from google.adk.sessions import InMemorySessionService

# Create agent to evaluate
agent = Agent(
    name="test_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant."
)

# Initialize evaluator
evaluator = Evaluator(
    agent=agent,
    session_service=InMemorySessionService()
)

# Run evaluation
async def evaluate():
    results = await evaluator.evaluate(
        eval_cases=eval_cases,
        app_name="test_app"
    )

    for result in results:
        print(f"Case: {result.eval_case.query}")
        print(f"Score: {result.score}")
        print(f"Status: {result.status}")

    return results
```

### CLI Evaluation

```bash
# Evaluate agent with test cases
adk eval path/to/agent path/to/evalset.json

# Evaluate with specific criteria
adk eval path/to/agent evalset.json --criteria response_match_score:0.8

# Generate evaluation report
adk eval path/to/agent evalset.json --output results.json

# Create a new eval set
adk eval create-set path/to/evalset.json

# Add an eval case to existing set
adk eval add-case path/to/evalset.json --query "What is 2+2?" --expected "4"
```

---

## Deployment

### Cloud Run Deployment

```bash
# Deploy to Cloud Run
adk deploy cloud-run path/to/agent \
  --project my-project \
  --region us-central1

# Deploy with UI and A2A
adk deploy cloud_run \
  --project=your-project-id \
  --region=us-central1 \
  --service_name=my-agent-service \
  --with_ui \
  --a2a \
  ./my_agent
```

### Vertex AI Agent Engine

```bash
# Deploy to Vertex AI Agent Engine
adk deploy agent-engine path/to/agent \
  --project my-project \
  --location us-central1 \
  --display-name "My Agent"
```

### Docker Deployment

```bash
# Build Docker container
adk deploy docker path/to/agent \
  --output Dockerfile
```

### FastAPI Server

```bash
# Start API server
adk api_server path/to/agents_dir
```

### Programmatic FastAPI

```python
from google.adk.cli.fast_api import get_fast_api_app

app = get_fast_api_app(agent_dir="./agents")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

---

## CLI Commands

### Development

```bash
# Install ADK
pip install google-adk

# Run agent interactively
adk run path/to/agent

# Run with specific input file
adk run path/to/agent --input input.json

# Start development UI
adk web path/to/agent

# Start development UI with custom port
adk web path/to/agent --port 8080
```

### Testing

```bash
# Run tests
pytest tests/unittests

# Run tests in parallel
pytest tests/unittests -n auto

# Run specific test file
pytest tests/unittests/agents/test_llm_agent.py
```

### Code Quality

```bash
# Format code with pyink
pyink --config pyproject.toml src/ tests/ contributing/

# Format imports with isort
isort src/ tests/ contributing/

# Check code formatting
pyink --check src/
isort --check src/
```

---

## Advanced Patterns

### Context Caching

```python
from google.adk import Agent
from google.adk.agents import ContextCacheConfig
from google.adk.apps import App
from google.genai import types

# Create agent with static instruction for caching
agent = Agent(
    name="cached_agent",
    model="gemini-2.5-flash",
    static_instruction=types.Content(
        parts=[types.Part(text="You are an expert in Python programming. " * 100)]
    ),
    instruction="Answer Python programming questions."
)

# Configure context caching at app level
app = App(
    name="cached_app",
    root_agent=agent,
    context_cache_config=ContextCacheConfig(
        enable_auto_caching=True,
        ttl_seconds=3600
    )
)
```

### Debugging with run_debug()

```python
from google.adk.sessions import InMemorySessionService

# Simplified debugging
runner = InMemoryRunner(agent=agent)
await runner.run_debug("Hi")

# With verbose output
await runner.run_debug("Query", verbose=True)

# Multiple queries
await runner.run_debug(["Query 1", "Query 2", "Query 3"])

# Custom session
await runner.run_debug(
    "Hello",
    user_id="alice",
    session_id="debug_session"
)

# Capture events without printing
events = await runner.run_debug("Process this", quiet=True)

# Maintain session state
await runner.run_debug("First query", user_id="alice", session_id="debug")
await runner.run_debug("Follow-up", user_id="alice", session_id="debug")
```

### LiteLLM Integration (Ollama)

```python
from google.adk import Agent
from google.adk.models import LiteLlm

# Using ollama_chat provider (recommended)
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    name="dice_agent",
    description="Agent that can roll dice.",
    instruction="You roll dice and answer questions.",
    tools=[roll_die, check_prime]
)

# Using openai provider with Ollama
root_agent = Agent(
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description="Agent that can roll dice.",
    instruction="You roll dice and answer questions.",
    tools=[roll_die, check_prime]
)
```

```bash
# Set environment variables for Ollama
export OLLAMA_API_BASE="http://localhost:11434"
adk web

# Or for OpenAI compatibility
export OPENAI_API_BASE=http://localhost:11434/v1
export OPENAI_API_KEY=anything
adk web
```

### Asynchronous Tools for Parallelism

```python
import asyncio

# ❌ Wrong - blocks the GIL, forces sequential execution
def my_tool():
    time.sleep(2)  # Blocks entire event loop

# ✅ Correct - allows true parallelism
async def my_tool():
    await asyncio.sleep(2)  # Non-blocking, parallel-friendly
```

### Tool Callbacks

Tool callbacks enable custom behavior modification before and after tool execution, allowing logging, validation, and error handling:

```python
from google.adk import Agent
from google.adk.tools import CallbackConfig, ToolConfig

# Define callback functions
async def before_tool_call(tool_name: str, args: dict) -> dict:
    """Execute before tool invocation."""
    print(f"Calling tool: {tool_name} with args: {args}")
    return args  # Can modify args

async def after_tool_call(tool_name: str, result: any) -> any:
    """Execute after tool completes."""
    print(f"Tool {tool_name} returned: {result}")
    return result  # Can transform result

# Create tool with callbacks
search_tool = ToolConfig(
    function=google_search,
    name="search",
    before_call=before_tool_call,
    after_call=after_tool_call,
    description="Search the web"
)

agent = Agent(
    name="callback_agent",
    model="gemini-2.5-flash",
    instruction="Use tools with callbacks for audit logging.",
    tools=[search_tool]
)
```

### Model Callbacks

Model callbacks provide hooks into the LLM call lifecycle for monitoring, caching, and behavior modification:

```python
from google.adk import Agent
from google.adk.models import ModelCallback

# Define model callbacks
class AuditModelCallback(ModelCallback):
    async def before_call(self, request):
        """Log request details before model call."""
        print(f"Model request: {request.model}")
        print(f"Messages: {len(request.messages)}")
        return request
    
    async def after_call(self, response):
        """Log response after model call."""
        print(f"Model responded with {len(response.content.parts)} parts")
        return response
    
    async def on_error(self, error):
        """Handle model call errors."""
        print(f"Model error: {error}")
        raise error

# Create agent with model callbacks
agent = Agent(
    name="audited_agent",
    model="gemini-2.5-flash",
    instruction="Execute queries with model callbacks.",
    callbacks=[AuditModelCallback()]
)
```

### Plugins for Context Management

Plugins extend agent functionality by managing context, chat history, and session state:

```python
from google.adk.plugins import Plugin, ContextFilterPlugin

# Custom context filter plugin
class SecretFilterPlugin(ContextFilterPlugin):
    async def filter_content(self, content):
        """Remove sensitive information from context."""
        if content and content.parts:
            for part in content.parts:
                if hasattr(part, 'text') and part.text:
                    # Redact API keys
                    part.text = part.text.replace(
                        r'api[_-]?key[:\s]*["\']?([a-zA-Z0-9_-]+)["\']?',
                        '[REDACTED]',
                        flags=re.IGNORECASE
                    )
        return content

# Chat history plugin
class ChatHistoryPlugin(Plugin):
    async def on_session_created(self, session_id):
        """Initialize session history."""
        print(f"Session created: {session_id}")
    
    async def on_message(self, message, session_id):
        """Log all messages."""
        print(f"Session {session_id}: {message.text[:50]}...")

# Use plugins in agent
agent = Agent(
    name="plugin_agent",
    model="gemini-2.5-flash",
    instruction="Process queries with plugin support.",
    plugins=[SecretFilterPlugin(), ChatHistoryPlugin()]
)
```

### FastMCP Integration

FastMCP enables rapid creation of MCP servers that expose ADK agents as standardized tools:

```python
from fastmcp import FastMCP
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService

# Create FastMCP server
mcp = FastMCP(name="adk_agent_server")

# Initialize ADK agent
agent = Agent(
    name="analysis_agent",
    model="gemini-2.5-flash",
    instruction="Analyze data and provide insights.",
    tools=[data_analysis_tool]
)

runner = Runner(
    app_name="analysis_app",
    agent=agent,
    session_service=InMemorySessionService()
)

# Expose agent as MCP tool
@mcp.tool()
async def analyze_data(query: str, dataset: str) -> str:
    """Analyze dataset based on query using ADK agent."""
    result = None
    async for event in runner.run_async(
        user_id="mcp_client",
        session_id="analysis_session",
        new_message=types.Content(
            role='user',
            parts=[types.Part(text=f"Analyze {dataset}: {query}")]
        )
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    result = part.text
    return result or "Analysis complete"

# Start FastMCP server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp, host="0.0.0.0", port=8000)
```

### LiteLLM Context Caching

LiteLLM enables context caching for alternative LLM providers (Ollama, OpenRouter), reducing latency and costs:

```python
from google.adk import Agent
from google.adk.models import LiteLlm, ContextCacheConfig

# Configure caching with LiteLLM
cache_config = ContextCacheConfig(
    enable_auto_caching=True,
    ttl_seconds=3600,
    min_cache_tokens=1024  # Minimum tokens to enable caching
)

# Create cached agent with Ollama via LiteLLM
cached_agent = Agent(
    name="cached_ollama_agent",
    model=LiteLlm(
        model="ollama/mistral",
        cache_config=cache_config
    ),
    static_instruction=types.Content(
        parts=[types.Part(text="You are an expert analyst. " * 50)]
    ),
    instruction="Answer questions using cached context."
)

# Or with OpenRouter
openrouter_agent = Agent(
    name="cached_openrouter_agent",
    model=LiteLlm(
        model="openrouter/meta-llama/llama-2-70b",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        cache_config=cache_config
    ),
    instruction="Process queries with caching enabled."
)

# Cache statistics
async def check_cache_stats():
    # Monitor cache hits and misses
    stats = await cached_agent.get_cache_stats()
    print(f"Cache hits: {stats['hits']}")
    print(f"Cache misses: {stats['misses']}")
    print(f"Cached tokens: {stats['cached_tokens']}")
```

---

## Model Context Protocol (MCP) Integration

### What is MCP?

The Model Context Protocol (MCP) is an open standard for connecting AI agents to external tools, data sources, and services. It enables standardized communication between AI applications and various servers/services.

### MCP in ADK

ADK seamlessly integrates with MCP servers, allowing agents to dynamically discover and use tools exposed by MCP servers.

### Creating MCP Toolsets

```python
from google.adk import Agent
from mcp.client.stdio import StdioServerParameters
from google.adk.tools.mcp_toolset import MCPToolset

async def get_tools_from_mcp():
    """Fetch tools from an MCP server."""
    server_params = StdioServerParameters(
        command="mcp-flight-search",
        args=["--connection_type", "stdio"],
        env={"SERP_API_KEY": os.getenv("SERP_API_KEY")}
    )
    
    # Create MCP toolset
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=server_params
    )
    return tools, exit_stack

async def create_mcp_agent():
    tools, exit_stack = await get_tools_from_mcp()
    
    agent = Agent(
        name="mcp_agent",
        model="gemini-2.5-flash",
        instruction="Use MCP tools to search for flights.",
        tools=tools
    )
    
    return agent, exit_stack
```

### Running ADK Agent with MCP Server

```bash
# Start MCP server
mcp-flight-search --connection_type stdio

# In another terminal, run ADK agent
adk run flight_search_agent
```

### Exposing ADK Agent as MCP Server

```python
from google.adk.apps import App
from fastmcp import FastMCP

app = App(name="my_app", root_agent=root_agent)
mcp = FastMCP(name="adk_server")

# Expose agent as MCP server tool
@mcp.tool()
async def run_agent(query: str) -> str:
    """Run the ADK agent with a query."""
    result = await runner.run_async(
        user_id="mcp_client",
        session_id="mcp_session",
        new_message=types.Content(
            role='user',
            parts=[types.Part(text=query)]
        )
    )
    return result
```

### MCP Database Integration Example

```python
# FastMCP Server exposing database tools
from fastmcp import FastMCP
import sqlite3

mcp = FastMCP(name="database_mcp")

@mcp.tool()
def list_db_tables(dummy_param: str) -> dict:
    """List all tables in the database."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return {"tables": tables}

@mcp.tool()
def query_db_table(table_name: str, columns: str, condition: str) -> list:
    """Query a database table."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if columns == "*":
        query = f"SELECT * FROM {table_name}"
    else:
        query = f"SELECT {columns} FROM {table_name}"
    
    if condition and condition != "1=1":
        query += f" WHERE {condition}"
    
    cursor.execute(query)
    results = [dict(zip([col[0] for col in cursor.description], row)) 
               for row in cursor.fetchall()]
    conn.close()
    return results

@mcp.tool()
def insert_data(table_name: str, data: dict) -> dict:
    """Insert data into a table."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data.keys()])
    values = list(data.values())
    
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "Data inserted"}
```

---

## Multi-Agent Patterns

### Pattern Overview

ADK supports several multi-agent orchestration patterns for building complex, collaborative AI systems.

### Hierarchical Multi-Agent System

Specialized agents report to a coordinator that delegates tasks.

```python
from google.adk.agents import LlmAgent

# Define specialized agents
linkedin_agent = LlmAgent(
    name="linkedin_specialist",
    model="gemini-2.5-flash",
    description="Searches and analyzes LinkedIn data.",
    instruction="Find and analyze LinkedIn profiles and data.",
    tools=[linkedin_search_tool]
)

notion_agent = LlmAgent(
    name="notion_specialist",
    model="gemini-2.5-flash",
    description="Manages Notion workspace data.",
    instruction="Read and manage Notion pages and databases.",
    tools=[notion_tool]
)

research_agent = LlmAgent(
    name="research_specialist",
    model="gemini-2.5-flash",
    description="Performs deep research tasks.",
    instruction="Conduct thorough research using available tools.",
    tools=[google_search]
)

# Create coordinator
coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.5-flash",
    description="Orchestrates specialized agents.",
    instruction="""You are a coordinator that delegates tasks to specialized agents.
    - For LinkedIn data: delegate to linkedin_specialist
    - For Notion data: delegate to notion_specialist  
    - For research: delegate to research_specialist
    
    Combine their results into a comprehensive response.""",
    sub_agents=[linkedin_agent, notion_agent, research_agent]
)
```

### Parallel Processing Pattern

Fan-out tasks to multiple agents, then aggregate results.

```python
from google.adk.agents import ParallelAgent, LlmAgent

# Create specialized analyzers
grammar_checker = LlmAgent(
    name="grammar_checker",
    model="gemini-2.5-flash",
    instruction="Check grammar, spelling, and punctuation."
)

fact_checker = LlmAgent(
    name="fact_checker",
    model="gemini-2.5-flash",
    instruction="Verify factual accuracy and consistency.",
    tools=[google_search]
)

style_analyzer = LlmAgent(
    name="style_analyzer",
    model="gemini-2.5-flash",
    instruction="Analyze writing style, tone, and clarity."
)

# Parallel processor
parallel_analyzer = ParallelAgent(
    name="content_analyzer",
    description="Analyze content from multiple perspectives simultaneously.",
    sub_agents=[grammar_checker, fact_checker, style_analyzer]
)
```

### Sequential Workflow Pattern

Agents execute in a specific sequence, passing results forward.

```python
from google.adk.agents import SequentialAgent, LlmAgent

# Step 1: Research
research_agent = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="Conduct thorough research on the topic.",
    tools=[google_search, url_context]
)

# Step 2: Write
writer_agent = LlmAgent(
    name="writer",
    model="gemini-2.5-flash",
    instruction="Write comprehensive content based on research findings.",
)

# Step 3: Edit
editor_agent = LlmAgent(
    name="editor",
    model="gemini-2.5-flash",
    instruction="Edit and polish the content for publication.",
)

# Sequential pipeline
content_pipeline = SequentialAgent(
    name="content_production",
    description="Research → Write → Edit content pipeline",
    sub_agents=[research_agent, writer_agent, editor_agent]
)
```

### Iterative Refinement Pattern

Agent repeatedly improves output through multiple iterations.

```python
from google.adk.agents import LoopAgent, LlmAgent

refinement_agent = LlmAgent(
    name="refinement_agent",
    model="gemini-2.5-flash",
    instruction="""Improve the provided solution iteratively.
    
    For each iteration:
    1. Analyze the current solution
    2. Identify areas for improvement
    3. Suggest enhancements
    4. Implement improvements
    5. If quality is excellent, call exit_loop; otherwise continue""",
    tools=[exit_loop]
)

iterative_improver = LoopAgent(
    name="iterative_improver",
    description="Refine solutions through multiple iterations",
    sub_agents=[refinement_agent],
    max_iterations=5
)
```

### Router Pattern

Intelligent routing of tasks to appropriate agents based on analysis.

```python
from google.adk.agents import LlmAgent

# Specialized agents
support_agent = LlmAgent(
    name="support_agent",
    model="gemini-2.5-flash",
    description="Handles customer support requests",
    instruction="Provide helpful customer support."
)

billing_agent = LlmAgent(
    name="billing_agent",
    model="gemini-2.5-flash",
    description="Handles billing inquiries",
    instruction="Handle billing and account questions."
)

technical_agent = LlmAgent(
    name="technical_agent",
    model="gemini-2.5-flash",
    description="Handles technical issues",
    instruction="Resolve technical problems.",
    tools=[google_search]
)

# Router
router = LlmAgent(
    name="router",
    model="gemini-2.5-flash",
    description="Routes requests to appropriate agents",
    instruction="""Analyze the incoming request and route it:
    - For general support: route to support_agent
    - For billing issues: route to billing_agent
    - For technical problems: route to technical_agent
    
    Provide the routed response to the user.""",
    sub_agents=[support_agent, billing_agent, technical_agent]
)
```

---

## Agent-to-Agent Communication

### A2A Overview

Agent-to-Agent (A2A) Communication enables independent agents to communicate and collaborate through standardized protocols.

### A2A Architecture

```python
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.apps import App
import asyncio

# Define independent agents
analyst_agent = Agent(
    name="analyst",
    model="gemini-2.5-flash",
    description="Performs data analysis",
    instruction="Analyze data and provide insights.",
    tools=[analysis_tools]
)

writer_agent = Agent(
    name="writer",
    model="gemini-2.5-flash",
    description="Writes reports",
    instruction="Write comprehensive reports based on analysis.",
)

# Create separate runners for each agent
analyst_runner = Runner(
    app_name="analyst_app",
    agent=analyst_agent,
    session_service=InMemorySessionService()
)

writer_runner = Runner(
    app_name="writer_app",
    agent=writer_agent,
    session_service=InMemorySessionService()
)

# A2A Communication
async def a2a_workflow():
    # Analyst agent processes data
    analysis_result = None
    async for event in analyst_runner.run_async(
        user_id="workflow",
        session_id="session1",
        new_message=types.Content(
            role='user',
            parts=[types.Part(text="Analyze the Q4 sales data")]
        )
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    analysis_result = part.text
    
    # Writer agent uses analysis results
    if analysis_result:
        async for event in writer_runner.run_async(
            user_id="workflow",
            session_id="session2",
            new_message=types.Content(
                role='user',
                parts=[types.Part(text=f"Write a report based on this analysis: {analysis_result}")]
            )
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"Report: {part.text}")
```

### A2A with Service Registry

```python
# Agents register themselves in a service registry
class AgentRegistry:
    _agents = {}
    
    @classmethod
    def register(cls, name: str, agent: Agent, runner: Runner):
        cls._agents[name] = {"agent": agent, "runner": runner}
    
    @classmethod
    def get_agent(cls, name: str) -> tuple:
        return cls._agents.get(name)
    
    @classmethod
    def list_agents(cls):
        return list(cls._agents.keys())

# Register agents
AgentRegistry.register("analyst", analyst_agent, analyst_runner)
AgentRegistry.register("writer", writer_agent, writer_runner)

# Request service from another agent
async def request_analysis(data: str) -> str:
    agent_info = AgentRegistry.get_agent("analyst")
    if agent_info:
        runner = agent_info["runner"]
        async for event in runner.run_async(
            user_id="service_request",
            session_id="req1",
            new_message=types.Content(
                role='user',
                parts=[types.Part(text=data)]
            )
        ):
            if event.content and event.content.parts:
                return "".join(part.text for part in event.content.parts if part.text)
```

### A2A via Cloud Run

Deploy multiple agents to separate Cloud Run services and communicate via HTTP.

```bash
# Deploy analyst agent to Cloud Run
adk deploy cloud-run path/to/analyst_agent \
  --project my-project \
  --region us-central1 \
  --service_name analyst-agent

# Deploy writer agent to Cloud Run
adk deploy cloud-run path/to/writer_agent \
  --project my-project \
  --region us-central1 \
  --service_name writer-agent
```

```python
import httpx

async def call_remote_agent(agent_url: str, query: str) -> str:
    """Call another agent via HTTP."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{agent_url}/run",
            json={
                "user_id": "a2a_caller",
                "session_id": "session123",
                "message": query
            }
        )
        result = response.json()
        return result.get("response", "")

# Usage
analyst_response = await call_remote_agent(
    "https://analyst-agent-xxx.run.app",
    "Analyze Q4 sales data"
)

writer_response = await call_remote_agent(
    "https://writer-agent-xxx.run.app",
    f"Write report based on: {analyst_response}"
)
```

### A2A State Sharing

Share state between agents through a central state service.

```python
from typing import Dict, Any

class SharedStateService:
    """Shared state for A2A communication."""
    _state: Dict[str, Any] = {}
    
    @classmethod
    def set_state(cls, key: str, value: Any):
        cls._state[key] = value
    
    @classmethod
    def get_state(cls, key: str) -> Any:
        return cls._state.get(key)
    
    @classmethod
    def update_state(cls, key: str, updates: Dict[str, Any]):
        if key in cls._state:
            cls._state[key].update(updates)
    
    @classmethod
    def clear_state(cls):
        cls._state.clear()

# Analyst agent stores results in shared state
async def analyst_workflow():
    # ... analysis code ...
    SharedStateService.set_state("analysis_results", {
        "revenue": 1000000,
        "growth": "15%",
        "trend": "positive"
    })

# Writer agent retrieves from shared state
async def writer_workflow():
    analysis = SharedStateService.get_state("analysis_results")
    # Use analysis to write report
```



### Required Directory Structure

```text
my_adk_project/
└── src/
    └── my_app/
        ├── agents/
        │   ├── my_agent/
        │   │   ├── __init__.py   # MUST contain: from . import agent
        │   │   └── agent.py      # MUST define: root_agent = Agent(...) OR app = App(...)
        │   └── another_agent/
        │       ├── __init__.py
        │       └── agent.py
```

### agent.py Template

```python
# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# ...

from __future__ import annotations  # REQUIRED - Always include this

from google.adk import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    description="Agent description.",
    tools=[google_search]
)
```

### __init__.py Template

```python
from . import agent
```

---

## Configuration

### Environment Variables

```bash
# Gemini Developer API
export GEMINI_API_KEY='your-api-key'

# Vertex AI
export GOOGLE_GENAI_USE_VERTEXAI=True
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='us-central1'

# LiteLLM with Ollama
export OLLAMA_API_BASE="http://localhost:11434"

# OAuth2 Configuration
export CONNECTION_NAME=<YOUR_CONNECTION_NAME>
export CONNECTION_PROJECT=<YOUR_PROJECT_ID>
export CONNECTION_LOCATION=<YOUR_LOCATION>
```

### Agent YAML Configuration

```yaml
# root_agent.yaml
env:
  OPENAPI_MCP_HEADERS: '{"Authorization": "Bearer secret_token", "Notion-Version": "2022-06-28"}'
```

### .env File Template

```bash
# Choose Model Backend: 0 -> ML Dev, 1 -> Vertex
GOOGLE_GENAI_USE_VERTEXAI=1

# ML Dev backend config
GOOGLE_API_KEY=your_google_api_key_here

# Vertex backend config
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

---

## Best Practices

### 1. Always Use Future Annotations

```python
from __future__ import annotations  # REQUIRED - Always include this
```

### 2. Use Async Tools for Parallelism

```python
# ✅ Correct
async def my_tool():
    await asyncio.sleep(2)
```

### 3. Maintain Session State

```python
# Use consistent user_id and session_id
await runner.run_debug("First query", user_id="alice", session_id="debug")
await runner.run_debug("Follow-up", user_id="alice", session_id="debug")
```

### 4. Enable Resumability for Long Tasks

```python
app = App(
    name="resumable_app",
    root_agent=agent,
    resumability_config=ResumabilityConfig(is_resumable=True)
)
```

### 5. Use Plugins for Context Management

```python
from google.adk.plugins import ContextFilterPlugin

app = App(
    name="my_app",
    root_agent=agent,
    plugins=[
        ContextFilterPlugin(num_invocations_to_keep=3)
    ]
)
```

### 6. Test Before Deployment

```bash
# Run evaluations
adk eval path/to/agent path/to/evalset.json

# Test locally with web UI
adk web path/to/agent
```

### 7. Use Environment Variables for Secrets

```python
import os

api_key = os.getenv('GOOGLE_API_KEY')
project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
```

### 8. Enable Debugging When Needed

```python
# For LiteLLM
import litellm
litellm._turn_on_debug()

# For ADK
await runner.run_debug("Query", verbose=True)
```

### 9. Structure Multi-Agent Systems Logically

```python
# Use hierarchical organization
coordinator = LlmAgent(
    name="coordinator",
    sub_agents=[specialist1, specialist2, specialist3]
)
```

### 10. Document Your Tools

```python
def my_tool(param: str) -> str:
    """Clear description of what the tool does.

    Args:
        param: Description of parameter.

    Returns:
        Description of return value.
    """
    pass
```

---

## Quick Start Examples

### Basic Agent

```python
from google.adk import Agent, Runner
from google.adk.tools import google_search
from google.adk.sessions import InMemorySessionService
from google.genai import types

agent = Agent(
    name="assistant",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    tools=[google_search]
)

runner = Runner(
    app_name="my_app",
    agent=agent,
    session_service=InMemorySessionService()
)

async def main():
    content = types.Content(
        role='user',
        parts=[types.Part(text="What's the weather in Tokyo?")]
    )
    async for event in runner.run_async(
        user_id="user123",
        session_id="session456",
        new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)
```

### Multi-Agent System

```python
from google.adk.agents import LlmAgent

# Specialized agents
researcher = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="Research topics thoroughly.",
    tools=[google_search]
)

writer = LlmAgent(
    name="writer",
    model="gemini-2.5-flash",
    instruction="Write based on research."
)

# Coordinator
coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.5-flash",
    instruction="Coordinate research and writing.",
    sub_agents=[researcher, writer]
)
```

### Debugging

```python
from google.adk.sessions import InMemorySessionService

runner = InMemoryRunner(agent=agent)
await runner.run_debug("What's the weather?")
```

---

## Resources

- **GitHub Repository**: https://github.com/google/adk-python
- **Documentation**: https://google.github.io/adk-docs
- **Samples**: https://github.com/google/adk-samples
- **Community**: Google ADK Discussion Forums

---

## Version History

- **v1.8.0** - Current stable release
- **v1.7.0** - Added context caching support
- **v1.6.0** - Multi-agent improvements
- **v1.0.0** - Initial stable release

---

**Generated from Context7 Documentation**  
**Date**: November 8, 2025
