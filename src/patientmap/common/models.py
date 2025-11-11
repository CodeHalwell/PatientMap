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
    node_type: str = Field(..., description="Type of node (patient, condition, medication, research_article, clinical_trial)")
    properties: Optional[dict[str, str]] = Field(None, description="Additional properties of the graph node")

class GraphEdge(BaseModel):
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship: str = Field(..., description="Type of relationship between source and target nodes")

class KnowledgeGraph(BaseModel):
    """Simplified KG model for Gemini API compatibility - avoids nested Pydantic models"""
    node_ids: list[str] = Field(..., description="List of node IDs in the knowledge graph")
    node_labels: list[str] = Field(..., description="List of node labels corresponding to node_ids")
    node_types: list[str] = Field(..., description="List of node types corresponding to node_ids")
    edge_sources: list[str] = Field(..., description="List of source node IDs for edges")
    edge_targets: list[str] = Field(..., description="List of target node IDs for edges")
    edge_relationships: list[str] = Field(..., description="List of relationship types for edges")
    description: str = Field(..., description="High-level description of the knowledge graph plan")

class MedicalCondition(BaseModel):
    name: str = Field(..., description="Name of the medical condition")
    icd_code: Optional[str] = Field(None, description="ICD code for the medical condition")
    symptoms: Optional[list[str]] = Field(None, description="List of symptoms associated with the condition")
    treatments: Optional[list[str]] = Field(None, description="List of treatments for the condition")
    description: Optional[str] = Field(None, description="Detailed description of the medical condition")

class MedicationInfo(BaseModel):
    name: str = Field(..., description="Name of the medication")
    dosage: Optional[str] = Field(None, description="Dosage information for the medication")
    side_effects: Optional[list[str]] = Field(None, description="List of known side effects for the medication")
    interactions: Optional[list[str]] = Field(None, description="List of known drug interactions for the medication")
    usage_instructions: Optional[str] = Field(None, description="Instructions for using the medication")

class PatientRecord(BaseModel):
    patient_id: str = Field(..., description="Unique identifier for the patient")
    name: str = Field(..., description="Name of the patient")
    age: Optional[int] = Field(None, description="Age of the patient")
    medical_history: Optional[list[str]] = Field(None, description="List of medical history entries for the patient")
    medications: Optional[list[str]] = Field(None, description="List of current medications for the patient")
    allergies: Optional[list[str]] = Field(None, description="List of known allergies for the patient")
    conditions: Optional[list[str]] = Field(None, description="List of diagnosed medical conditions for the patient")
    notes: Optional[str] = Field(None, description="Additional notes about the patient")

class MedicalResearchArticle(BaseModel):
    title: str = Field(..., description="Title of the research article")
    authors: Optional[list[str]] = Field(None, description="List of authors of the article")
    publication_date: Optional[str] = Field(None, description="Publication date of the article")
    keywords: Optional[list[str]] = Field(None, description="List of keywords associated with the article")
    topics: Optional[list[str]] = Field(None, description="List of topics covered in the article")
    related_conditions: Optional[list[MedicalCondition]] = Field(None, description="List of medical conditions related to the article")
    journal: Optional[str] = Field(None, description="Journal where the article was published")
    abstract: Optional[str] = Field(None, description="Abstract of the research article")
    url: Optional[str] = Field(None, description="URL to access the full article")