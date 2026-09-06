import re

from pydantic import BaseModel, Field
from typing import Optional

# Gemini model IDs this project is validated against, newest first. Enumerated
# rather than shape-matched so an unsupported ID fails when the agent config is
# loaded instead of on the first generation request — note that there is no
# gemini-3.8-pro, so a plausible-looking ID is not necessarily a real one.
# Refresh from https://ai.google.dev/gemini-api/docs/models when Google ships a
# new release; this tuple is the only place that needs editing.
SUPPORTED_MODELS: tuple[str, ...] = (
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
)

DEFAULT_MODEL: str = SUPPORTED_MODELS[0]

_SUPPORTED_MODEL_PATTERN = f"^({'|'.join(re.escape(m) for m in SUPPORTED_MODELS)})$"

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
        default=DEFAULT_MODEL,
        description=f"Model used by the agent. One of: {', '.join(SUPPORTED_MODELS)}",
        pattern=_SUPPORTED_MODEL_PATTERN
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
    """Simplified KG model for Gemini API compatibility - avoids nested Pydantic models
    
    Note: For planning purposes, focus on high-level structure with representative examples
    rather than exhaustive enumeration of all nodes/edges.
    """
    node_ids: list[str] = Field(..., description="List of key representative node IDs (limit to ~20 essential nodes)")
    node_labels: list[str] = Field(..., description="List of node labels corresponding to node_ids")
    node_types: list[str] = Field(..., description="List of node types corresponding to node_ids")
    edge_sources: list[str] = Field(..., description="List of source node IDs for key representative edges (limit to ~40 edges)")
    edge_targets: list[str] = Field(..., description="List of target node IDs for key representative edges")
    edge_relationships: list[str] = Field(..., description="List of relationship types for key representative edges")
    description: str = Field(..., description="High-level description of the knowledge graph plan and structure")

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