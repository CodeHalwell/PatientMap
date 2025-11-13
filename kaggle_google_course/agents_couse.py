import uuid
from google.genai import types
import asyncio

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, StdioServerParameters
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.apps.app import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool
from google.adk.runners import InMemoryRunner

from dotenv import load_dotenv

load_dotenv()

print("✅ ADK components imported successfully.")

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

import os
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

    
# Create the agent with MCP toolset
image_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="hugging_face_agent",
    instruction="Help users get information from Hugging Face",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@llmindset/hf-mcp-server",
                    ],
                    env={
                        "HF_TOKEN": HUGGING_FACE_TOKEN,
                    }
                ),
                timeout=60,
            ),
        )
    ],
)

print("✅ Agent with MCP toolset created successfully.")

# Define root_agent for ADK CLI compatibility
root_agent = image_agent

async def main():
    """Main function to run the agent."""
    import base64
    
    runner = InMemoryRunner(agent=image_agent)
    events = await runner.run_debug("Can you generate image of a cat", verbose=True)
    
    # Process events to find and save images
    image_count = 0
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                # Check for function responses with image data
                if hasattr(part, "function_response") and part.function_response:
                    response_data = part.function_response.response
                    if isinstance(response_data, dict):
                        # Handle different response formats
                        content = response_data.get("content", [])
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get("type") == "image":
                                    image_data = item.get("data")
                                    if image_data:
                                        # Save the image
                                        image_count += 1
                                        filename = f"cat_image_{image_count}.png"
                                        with open(filename, "wb") as f:
                                            f.write(base64.b64decode(image_data))
                                        print(f"✅ Image saved as: {filename}")
                        # Handle direct base64 in response
                        elif isinstance(response_data.get("image"), str):
                            image_count += 1
                            filename = f"cat_image_{image_count}.png"
                            with open(filename, "wb") as f:
                                f.write(base64.b64decode(response_data["image"]))
                            print(f"✅ Image saved as: {filename}")
                
                # Check for text responses
                if hasattr(part, "text") and part.text:
                    print(f"\n📝 Agent response: {part.text}")
    
    if image_count == 0:
        print("\n⚠️ No images were generated. Check the verbose output above for details.")
    
    return events

# Only run if executed directly (not imported by ADK CLI)
if __name__ == "__main__":
    response = asyncio.run(main())
    print(f"\n✅ Complete. Generated {sum(1 for e in response for p in (e.content.parts if e.content else []) if hasattr(p, 'function_response'))} responses.")

