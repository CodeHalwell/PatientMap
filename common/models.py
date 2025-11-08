from pydantic import BaseModel, Field
from typing import Optional

class Message(BaseModel):
    id: int = Field(..., description="Unique identifier for the message")
    content: str = Field(..., description="Content of the message")
    timestamp: Optional[str] = Field(None, description="Timestamp of when the message was sent")

class Response(BaseModel):
    id: int = Field(..., description="Unique identifier for the response")
    agent_name: str = Field(..., description="Name of the agent generating the response")
    content: str = Field(..., description="Content of the response")
    timestamp: Optional[str] = Field(None, description="Timestamp of when the response was generated")

class AgentSettings(BaseModel):
    agent_id: str = Field(..., description="Unique identifier for the agent")
    agent_name: str = Field(..., description="Name of the agent")
    model: str = Field(
        default="gemini-2.5-flash",
        description="Model used by the agent",
        pattern="^(gemini-2.5-pro|gemini-2.5-pro-preview-tts|gemini-2.5-flash|gemini-2.5-flash-preview-09-2025|gemini-2.5-flash-native-audio-preview-09-2025|gemini-2.5-flash-preview-tts|gemini-2.5-flash-lite|gemini-2.5-flash-lite-preview-09-2025)$"
    )
    instruction: str = Field(..., description="Instruction for the agent")
    description: str = Field(..., description="Description of the agent")
    tools: Optional[list] = Field(None, description="List of tools available to the agent")
