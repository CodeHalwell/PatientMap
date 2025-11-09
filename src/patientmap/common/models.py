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

class GraphNode(BaseModel):
    id: str = Field(..., description="Unique identifier for the graph node")
    label: str = Field(..., description="Label of the graph node")
    properties: Optional[dict] = Field(None, description="Additional properties of the graph node")

class GraphEdge(BaseModel):
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship: str = Field(..., description="Type of relationship between source and target nodes")

class KnowledgeGraph(BaseModel):
    nodes: list[GraphNode] = Field(..., description="List of nodes in the knowledge graph")
    edges: list[GraphEdge] = Field(..., description="List of edges in the knowledge graph")

class PatientRecord(BaseModel):
    patient_id: str = Field(..., description="Unique identifier for the patient")
    name: str = Field(..., description="Name of the patient")
    age: Optional[int] = Field(None, description="Age of the patient")
    medical_history: Optional[list[str]] = Field(None, description="List of medical history entries for the patient")
    medications: Optional[list[str]] = Field(None, description="List of current medications for the patient")
    allergies: Optional[list[str]] = Field(None, description="List of known allergies for the patient")
    conditions: Optional[list[str]] = Field(None, description="List of diagnosed conditions for the patient")
    metadata: Optional[dict] = Field(None, description="Additional metadata about the patient")