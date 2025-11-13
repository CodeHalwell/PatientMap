"""
Knowledge Graph Tools for PatientMap Agents

This module provides tools for creating, manipulating, and querying knowledge graphs
using NetworkX. These tools enable agents to build patient-centric knowledge graphs
and enrich them with research findings.
"""

from __future__ import annotations
import networkx as nx
from typing import Optional, Any
from google.adk.tools.tool_context import ToolContext
import json


# Helper functions for graph serialization

def _get_graph(tool_context: ToolContext) -> nx.DiGraph:
    """Get or create the knowledge graph from tool context.
    
    Deserializes from JSON if stored, otherwise creates new graph.
    """
    if 'kg_data' not in tool_context.state:
        return nx.DiGraph()
    
    # Deserialize from node_link_data format with explicit edges parameter
    data = tool_context.state['kg_data']
    return nx.node_link_graph(data, directed=True, edges="links")


def _save_graph(graph: nx.DiGraph, tool_context: ToolContext) -> None:
    """Save the knowledge graph to tool context in serializable format."""
    # Serialize to node_link_data format (JSON-compatible) with explicit edges parameter
    data = nx.node_link_data(graph, edges="links")
    tool_context.state['kg_data'] = data


# Graph initialization and management

def initialize_patient_graph(
    patient_id: str,
    patient_name: str,
    tool_context: ToolContext
) -> str:
    """Initialize a new knowledge graph for a patient.
    
    Args:
        patient_id: Unique identifier for the patient
        patient_name: Name of the patient
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message with patient node ID
    """
    graph = _get_graph(tool_context)
    
    # Add patient as central node
    graph.add_node(
        patient_id,
        node_type='patient',
        name=patient_name,
        label=f"Patient: {patient_name}"
    )
    
    _save_graph(graph, tool_context)
    
    return f"Initialized knowledge graph with patient node: {patient_id} ({patient_name})"


def add_node(
    node_id: str,
    node_type: str,
    label: str,
    properties: Optional[dict[str, Any]] = None,
    tool_context: ToolContext = None
) -> str:
    """Add a node to the knowledge graph.
    
    Args:
        node_id: Unique identifier for the node
        node_type: Type of node (e.g., 'condition', 'medication', 'symptom', 'research_article')
        label: Human-readable label for the node
        properties: Optional dictionary of additional properties
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message
    """
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized. Call initialize_patient_graph first."
    
    # Prepare node attributes
    attrs = {
        'node_type': node_type,
        'label': label
    }
    if properties:
        attrs.update(properties)
    
    graph.add_node(node_id, **attrs)
    _save_graph(graph, tool_context)
    
    return f"Added {node_type} node: {node_id} - {label}"


def bulk_add_nodes(
    nodes: list[dict[str, Any]],
    tool_context: ToolContext = None
) -> str:
    """Add multiple nodes to the knowledge graph in a single operation.
    
    This is more efficient than calling add_node multiple times when creating
    many nodes at once.
    
    Args:
        nodes: List of node dictionaries, each containing:
            - node_id (str): Unique identifier for the node
            - node_type (str): Type of node (e.g., 'condition', 'medication', 'symptom')
            - label (str): Human-readable label for the node
            - properties (dict, optional): Additional properties for the node
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message with count of nodes added
        
    Example:
        nodes = [
            {
                "node_id": "condition_diabetes",
                "node_type": "condition",
                "label": "Type 2 Diabetes",
                "properties": {"icd_code": "E11.9", "severity": "moderate"}
            },
            {
                "node_id": "medication_metformin",
                "node_type": "medication",
                "label": "Metformin",
                "properties": {"dosage": "500mg", "frequency": "BID"}
            }
        ]
    """
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized. Call initialize_patient_graph first."
    
    added_nodes = []
    errors = []
    
    for i, node_data in enumerate(nodes):
        try:
            # Validate required fields
            if 'node_id' not in node_data:
                errors.append(f"Node {i}: Missing required field 'node_id'")
                continue
            if 'node_type' not in node_data:
                errors.append(f"Node {i}: Missing required field 'node_type'")
                continue
            if 'label' not in node_data:
                errors.append(f"Node {i}: Missing required field 'label'")
                continue
            
            node_id = node_data['node_id']
            node_type = node_data['node_type']
            label = node_data['label']
            properties = node_data.get('properties', {})
            
            # Prepare node attributes
            attrs = {
                'node_type': node_type,
                'label': label
            }
            if properties:
                attrs.update(properties)
            
            # Add node to graph
            graph.add_node(node_id, **attrs)
            added_nodes.append(f"{node_type}: {label} ({node_id})")
            
        except Exception as e:
            errors.append(f"Node {i} ({node_data.get('node_id', 'unknown')}): {str(e)}")
    
    # Save graph once after all nodes added
    _save_graph(graph, tool_context)
    
    # Build result message
    result_parts = [f"Successfully added {len(added_nodes)} nodes to the knowledge graph."]
    
    if added_nodes:
        result_parts.append("\nNodes added:")
        for node_desc in added_nodes[:10]:  # Show first 10
            result_parts.append(f"  - {node_desc}")
        if len(added_nodes) > 10:
            result_parts.append(f"  ... and {len(added_nodes) - 10} more")
    
    if errors:
        result_parts.append(f"\n{len(errors)} errors encountered:")
        for error in errors[:5]:  # Show first 5 errors
            result_parts.append(f"  - {error}")
        if len(errors) > 5:
            result_parts.append(f"  ... and {len(errors) - 5} more errors")
    
    return "\n".join(result_parts)


def add_relationship(
    source_id: str,
    target_id: str,
    relationship_type: str,
    properties: Optional[dict[str, Any]] = None,
    tool_context: ToolContext = None
) -> str:
    """Add a relationship (edge) between two nodes in the knowledge graph.
    
    Args:
        source_id: ID of the source node
        target_id: ID of the target node
        relationship_type: Type of relationship (e.g., 'HAS_CONDITION', 'TAKES_MEDICATION', 'RELATED_TO')
        properties: Optional dictionary of edge properties (e.g., confidence, source)
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message
    """
    graph = _get_graph(tool_context)
    
    # Check if nodes exist
    if source_id not in graph:
        return f"Error: Source node '{source_id}' does not exist in the graph."
    if target_id not in graph:
        return f"Error: Target node '{target_id}' does not exist in the graph."
    
    # Prepare edge attributes
    attrs = {'relationship_type': relationship_type}
    if properties:
        attrs.update(properties)
    
    graph.add_edge(source_id, target_id, **attrs)
    _save_graph(graph, tool_context)
    
    return f"Added relationship: {source_id} --[{relationship_type}]--> {target_id}"


def bulk_add_relationships(
    relationships: list[dict[str, Any]],
    tool_context: ToolContext = None
) -> str:
    """Add multiple relationships to the knowledge graph in a single operation.
    
    This is more efficient than calling add_relationship multiple times when creating
    many edges at once.
    
    Args:
        relationships: List of relationship dictionaries, each containing:
            - source_id (str): ID of the source node
            - target_id (str): ID of the target node
            - relationship_type (str): Type of relationship (e.g., 'HAS_CONDITION', 'TAKES_MEDICATION')
            - properties (dict, optional): Additional properties for the edge
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message with count of relationships added
        
    Example:
        relationships = [
            {
                "source_id": "patient_123",
                "target_id": "condition_diabetes",
                "relationship_type": "HAS_CONDITION",
                "properties": {"onset_date": "2020-01-15"}
            },
            {
                "source_id": "patient_123",
                "target_id": "medication_metformin",
                "relationship_type": "TAKES_MEDICATION"
            }
        ]
    """
    graph = _get_graph(tool_context)
    
    added_relationships = []
    errors = []
    
    for i, rel_data in enumerate(relationships):
        try:
            # Validate required fields
            if 'source_id' not in rel_data:
                errors.append(f"Relationship {i}: Missing required field 'source_id'")
                continue
            if 'target_id' not in rel_data:
                errors.append(f"Relationship {i}: Missing required field 'target_id'")
                continue
            if 'relationship_type' not in rel_data:
                errors.append(f"Relationship {i}: Missing required field 'relationship_type'")
                continue
            
            source_id = rel_data['source_id']
            target_id = rel_data['target_id']
            relationship_type = rel_data['relationship_type']
            properties = rel_data.get('properties', {})
            
            # Check if nodes exist
            if source_id not in graph:
                errors.append(f"Relationship {i}: Source node '{source_id}' does not exist")
                continue
            if target_id not in graph:
                errors.append(f"Relationship {i}: Target node '{target_id}' does not exist")
                continue
            
            # Prepare edge attributes
            attrs = {'relationship_type': relationship_type}
            if properties:
                attrs.update(properties)
            
            # Add edge to graph
            graph.add_edge(source_id, target_id, **attrs)
            added_relationships.append(f"{source_id} --[{relationship_type}]--> {target_id}")
            
        except Exception as e:
            errors.append(f"Relationship {i}: {str(e)}")
    
    # Save graph once after all relationships added
    _save_graph(graph, tool_context)
    
    # Build result message
    result_parts = [f"Successfully added {len(added_relationships)} relationships to the knowledge graph."]
    
    if added_relationships:
        result_parts.append("\nRelationships added:")
        for rel_desc in added_relationships[:10]:  # Show first 10
            result_parts.append(f"  - {rel_desc}")
        if len(added_relationships) > 10:
            result_parts.append(f"  ... and {len(added_relationships) - 10} more")
    
    if errors:
        result_parts.append(f"\n{len(errors)} errors encountered:")
        for error in errors[:5]:  # Show first 5 errors
            result_parts.append(f"  - {error}")
        if len(errors) > 5:
            result_parts.append(f"  ... and {len(errors) - 5} more errors")
    
    return "\n".join(result_parts)


# Patient data integration

def add_patient_condition(
    patient_id: str,
    condition_name: str,
    icd_code: Optional[str] = None,
    symptoms: Optional[list[str]] = None,
    tool_context: ToolContext = None
) -> str:
    """Add a medical condition to the patient's knowledge graph.
    
    Args:
        patient_id: ID of the patient node
        condition_name: Name of the medical condition
        icd_code: Optional ICD code for the condition
        symptoms: Optional list of symptoms
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message
    """
    condition_id = f"condition_{condition_name.lower().replace(' ', '_')}"
    
    # Add condition node
    properties = {}
    if icd_code:
        properties['icd_code'] = icd_code
    if symptoms:
        properties['symptoms'] = symptoms
    
    result = add_node(
        node_id=condition_id,
        node_type='condition',
        label=condition_name,
        properties=properties,
        tool_context=tool_context
    )
    
    # Link patient to condition
    relationship_result = add_relationship(
        source_id=patient_id,
        target_id=condition_id,
        relationship_type='HAS_CONDITION',
        tool_context=tool_context
    )
    
    return f"{result}\n{relationship_result}"


def add_patient_medication(
    patient_id: str,
    medication_name: str,
    dosage: Optional[str] = None,
    side_effects: Optional[list[str]] = None,
    tool_context: ToolContext = None
) -> str:
    """Add a medication to the patient's knowledge graph.
    
    Args:
        patient_id: ID of the patient node
        medication_name: Name of the medication
        dosage: Optional dosage information
        side_effects: Optional list of side effects
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message
    """
    medication_id = f"medication_{medication_name.lower().replace(' ', '_')}"
    
    # Add medication node
    properties = {}
    if dosage:
        properties['dosage'] = dosage
    if side_effects:
        properties['side_effects'] = side_effects
    
    result = add_node(
        node_id=medication_id,
        node_type='medication',
        label=medication_name,
        properties=properties,
        tool_context=tool_context
    )
    
    # Link patient to medication
    relationship_result = add_relationship(
        source_id=patient_id,
        target_id=medication_id,
        relationship_type='TAKES_MEDICATION',
        tool_context=tool_context
    )
    
    return f"{result}\n{relationship_result}"


# Research integration

def add_research_article(
    article_title: str,
    authors: Optional[list[str]] = None,
    publication_date: Optional[str] = None,
    journal: Optional[str] = None,
    url: Optional[str] = None,
    abstract: Optional[str] = None,
    keywords: Optional[list[str]] = None,
    tool_context: ToolContext = None
) -> str:
    """Add a research article to the knowledge graph.
    
    Args:
        article_title: Title of the research article
        authors: Optional list of authors
        publication_date: Optional publication date
        journal: Optional journal name
        url: Optional URL to the article
        abstract: Optional abstract text
        keywords: Optional list of keywords
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message with article node ID
    """
    # Create unique article ID
    article_id = f"article_{hash(article_title) % 10**8}"
    
    properties = {'title': article_title}
    if authors:
        properties['authors'] = authors
    if publication_date:
        properties['publication_date'] = publication_date
    if journal:
        properties['journal'] = journal
    if url:
        properties['url'] = url
    if abstract:
        properties['abstract'] = abstract
    if keywords:
        properties['keywords'] = keywords
    
    result = add_node(
        node_id=article_id,
        node_type='research_article',
        label=article_title,
        properties=properties,
        tool_context=tool_context
    )
    
    return f"{result} (ID: {article_id})"


def link_article_to_condition(
    article_id: str,
    condition_id: str,
    relevance: str = "related",
    confidence: Optional[float] = None,
    tool_context: ToolContext = None
) -> str:
    """Link a research article to a medical condition.
    
    Args:
        article_id: ID of the research article node
        condition_id: ID of the condition node
        relevance: Type of relevance ('related', 'treatment', 'diagnosis', 'prognosis')
        confidence: Optional confidence score (0.0 to 1.0)
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message
    """
    properties = {'relevance': relevance}
    if confidence is not None:
        properties['confidence'] = confidence
    
    return add_relationship(
        source_id=article_id,
        target_id=condition_id,
        relationship_type='STUDIES',
        properties=properties,
        tool_context=tool_context
    )


def bulk_link_articles_to_conditions(
    links: list[dict[str, Any]],
    tool_context: ToolContext = None
) -> str:
    """Link multiple research articles to conditions in a single operation.
    
    This is much more efficient than calling link_article_to_condition repeatedly
    when you have many articles to link.
    
    Args:
        links: List of link dictionaries, each containing:
            - article_id (str): ID of the research article node
            - condition_id (str): ID of the condition node
            - relevance (str, optional): Type of relevance (default: 'related')
            - confidence (float, optional): Confidence score (0.0 to 1.0)
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message with count of links created
        
    Example:
        links = [
            {
                "article_id": "article_12345",
                "condition_id": "condition_diabetes",
                "relevance": "treatment",
                "confidence": 0.9
            },
            {
                "article_id": "article_67890",
                "condition_id": "condition_diabetes",
                "relevance": "diagnosis",
                "confidence": 0.85
            }
        ]
        bulk_link_articles_to_conditions(links)
    """
    graph = _get_graph(tool_context)
    
    relationships = []
    errors = []
    
    for i, link in enumerate(links):
        try:
            # Validate required fields
            if 'article_id' not in link:
                errors.append(f"Link {i}: Missing required field 'article_id'")
                continue
            if 'condition_id' not in link:
                errors.append(f"Link {i}: Missing required field 'condition_id'")
                continue
            
            article_id = link['article_id']
            condition_id = link['condition_id']
            relevance = link.get('relevance', 'related')
            confidence = link.get('confidence')
            
            # Check if nodes exist
            if article_id not in graph:
                errors.append(f"Link {i}: Article node '{article_id}' does not exist")
                continue
            if condition_id not in graph:
                errors.append(f"Link {i}: Condition node '{condition_id}' does not exist")
                continue
            
            # Build relationship
            properties = {'relevance': relevance}
            if confidence is not None:
                properties['confidence'] = confidence
            
            relationships.append({
                'source_id': article_id,
                'target_id': condition_id,
                'relationship_type': 'STUDIES',
                'properties': properties
            })
            
        except Exception as e:
            errors.append(f"Link {i}: {str(e)}")
    
    # Use bulk_add_relationships to add all at once
    if relationships:
        result = bulk_add_relationships(relationships, tool_context)
        
        if errors:
            result += "\n\nWarnings encountered:\n"
            for error in errors[:5]:
                result += f"  - {error}\n"
            if len(errors) > 5:
                result += f"  ... and {len(errors) - 5} more warnings\n"
        
        return result
    else:
        return "No valid article-condition links created. Errors:\n" + "\n".join(errors)


def add_clinical_trial(
    trial_id: str,
    trial_title: str,
    phase: Optional[str] = None,
    status: Optional[str] = None,
    conditions: Optional[list[str]] = None,
    interventions: Optional[list[str]] = None,
    url: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Add a clinical trial to the knowledge graph.
    
    Args:
        trial_id: Clinical trial identifier (e.g., NCT number)
        trial_title: Title of the clinical trial
        phase: Optional trial phase (e.g., 'Phase 3')
        status: Optional trial status (e.g., 'Recruiting', 'Completed')
        conditions: Optional list of conditions being studied
        interventions: Optional list of interventions being tested
        url: Optional URL to trial details
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message
    """
    properties = {'title': trial_title}
    if phase:
        properties['phase'] = phase
    if status:
        properties['status'] = status
    if conditions:
        properties['conditions'] = conditions
    if interventions:
        properties['interventions'] = interventions
    if url:
        properties['url'] = url
    
    result = add_node(
        node_id=trial_id,
        node_type='clinical_trial',
        label=trial_title,
        properties=properties,
        tool_context=tool_context
    )
    
    return f"{result}"


# Query and analysis tools

def get_patient_overview(
    patient_id: str,
    tool_context: ToolContext = None
) -> str:
    """Get a comprehensive overview of a patient's knowledge graph.
    
    Args:
        patient_id: ID of the patient node
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with patient overview including conditions, medications, and connected research
    """
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized."
    
    if patient_id not in graph:
        return f"Error: Patient '{patient_id}' not found in knowledge graph."
    
    # Get patient info
    patient_data = graph.nodes[patient_id]
    
    # Get conditions
    conditions = []
    for neighbor in graph.neighbors(patient_id):
        if graph.nodes[neighbor].get('node_type') == 'condition':
            edge_data = graph.get_edge_data(patient_id, neighbor)
            if edge_data.get('relationship_type') == 'HAS_CONDITION':
                conditions.append({
                    'id': neighbor,
                    'name': graph.nodes[neighbor].get('label'),
                    'icd_code': graph.nodes[neighbor].get('icd_code')
                })
    
    # Get medications
    medications = []
    for neighbor in graph.neighbors(patient_id):
        if graph.nodes[neighbor].get('node_type') == 'medication':
            edge_data = graph.get_edge_data(patient_id, neighbor)
            if edge_data.get('relationship_type') == 'TAKES_MEDICATION':
                medications.append({
                    'id': neighbor,
                    'name': graph.nodes[neighbor].get('label'),
                    'dosage': graph.nodes[neighbor].get('dosage')
                })
    
    # Count research articles
    condition_ids = [c['id'] for c in conditions]
    research_count = 0
    for condition_id in condition_ids:
        # Find articles linked to this condition
        predecessors = list(graph.predecessors(condition_id))
        research_count += sum(1 for pred in predecessors 
                            if graph.nodes[pred].get('node_type') == 'research_article')
    
    overview = {
        'patient_id': patient_id,
        'patient_name': patient_data.get('name'),
        'conditions': conditions,
        'medications': medications,
        'research_articles_count': research_count,
        'total_nodes': graph.number_of_nodes(),
        'total_relationships': graph.number_of_edges()
    }
    
    return json.dumps(overview, indent=2)


def find_related_research(
    condition_id: str,
    max_results: int = 10,
    tool_context: ToolContext = None
) -> str:
    """Find research articles related to a specific condition.
    
    Args:
        condition_id: ID of the condition node
        max_results: Maximum number of articles to return
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with list of related research articles
    """
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized."
    
    if condition_id not in graph:
        return f"Error: Condition '{condition_id}' not found in knowledge graph."
    
    # Find articles linked to this condition
    articles = []
    for predecessor in graph.predecessors(condition_id):
        if graph.nodes[predecessor].get('node_type') == 'research_article':
            edge_data = graph.get_edge_data(predecessor, condition_id)
            article_data = graph.nodes[predecessor]
            
            articles.append({
                'id': predecessor,
                'title': article_data.get('title') or article_data.get('label'),
                'authors': article_data.get('authors'),
                'journal': article_data.get('journal'),
                'url': article_data.get('url'),
                'relevance': edge_data.get('relevance'),
                'confidence': edge_data.get('confidence')
            })
    
    # Sort by confidence if available
    articles.sort(key=lambda x: x.get('confidence') or 0.5, reverse=True)
    
    result = {
        'condition_id': condition_id,
        'condition_name': graph.nodes[condition_id].get('label'),
        'articles': articles[:max_results],
        'total_found': len(articles)
    }
    
    return json.dumps(result, indent=2)


def export_graph_summary(tool_context: ToolContext = None) -> str:
    """Export a summary of the entire knowledge graph.
    
    Args:
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with graph statistics and node/edge counts by type
    """
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized."
    
    # Count nodes by type
    node_types = {}
    for node_id in graph.nodes():
        node_type = graph.nodes[node_id].get('node_type', 'unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    # Count edges by relationship type
    edge_types = {}
    for source, target in graph.edges():
        edge_data = graph.get_edge_data(source, target)
        rel_type = edge_data.get('relationship_type', 'unknown')
        edge_types[rel_type] = edge_types.get(rel_type, 0) + 1
    
    summary = {
        'total_nodes': graph.number_of_nodes(),
        'total_edges': graph.number_of_edges(),
        'nodes_by_type': node_types,
        'edges_by_type': edge_types,
        'is_directed': graph.is_directed()
    }
    
    return json.dumps(summary, indent=2)


# Graph validation and review tools

def validate_graph_structure(tool_context: ToolContext = None) -> str:
    """Validate the logical structure of the knowledge graph.
    
    Checks for:
    - Orphaned nodes (nodes with no connections)
    - Missing patient node
    - Nodes with missing required properties
    - Invalid relationship types
    
    Args:
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with validation results and issues found
    """
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized."
    
    issues = []
    warnings = []
    
    # Check for patient node
    patient_nodes = [n for n in graph.nodes() if graph.nodes[n].get('node_type') == 'patient']
    if not patient_nodes:
        issues.append("CRITICAL: No patient node found in the graph")
    elif len(patient_nodes) > 1:
        warnings.append(f"Multiple patient nodes found: {patient_nodes}")
    
    # Check for orphaned nodes (no connections)
    orphaned = []
    for node_id in graph.nodes():
        if graph.degree(node_id) == 0:
            node_label = graph.nodes[node_id].get('label', node_id)
            node_type = graph.nodes[node_id].get('node_type', 'unknown')
            orphaned.append(f"{node_type}: {node_label} (ID: {node_id})")
    
    if orphaned:
        warnings.append(f"Found {len(orphaned)} orphaned nodes with no connections: {orphaned[:5]}")
    
    # Check for nodes missing labels
    missing_labels = []
    for node_id in graph.nodes():
        if not graph.nodes[node_id].get('label'):
            node_type = graph.nodes[node_id].get('node_type', 'unknown')
            missing_labels.append(f"{node_type} (ID: {node_id})")
    
    if missing_labels:
        warnings.append(f"Found {len(missing_labels)} nodes missing labels: {missing_labels[:5]}")
    
    # Check for disconnected components
    if not nx.is_weakly_connected(graph):
        num_components = nx.number_weakly_connected_components(graph)
        issues.append(f"Graph has {num_components} disconnected components - should be fully connected")
    
    validation_result = {
        'is_valid': len(issues) == 0,
        'critical_issues': issues,
        'warnings': warnings,
        'total_issues': len(issues),
        'total_warnings': len(warnings)
    }
    
    return json.dumps(validation_result, indent=2)


def check_node_completeness(node_id: str, tool_context: ToolContext = None) -> str:
    """Check if a specific node has complete and valid information.
    
    Args:
        node_id: ID of the node to check
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with completeness analysis
    """
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized."
    
    if node_id not in graph:
        return f"Error: Node '{node_id}' not found in knowledge graph."
    
    node_data = graph.nodes[node_id]
    node_type = node_data.get('node_type', 'unknown')
    
    completeness = {
        'node_id': node_id,
        'node_type': node_type,
        'has_label': bool(node_data.get('label')),
        'property_count': len(node_data),
        'incoming_edges': graph.in_degree(node_id),
        'outgoing_edges': graph.out_degree(node_id),
        'issues': [],
        'suggestions': []
    }
    
    # Type-specific validation
    if node_type == 'patient':
        if not node_data.get('name'):
            completeness['issues'].append("Patient node missing 'name' property")
        if graph.out_degree(node_id) == 0:
            completeness['suggestions'].append("Patient has no conditions or medications linked")
    
    elif node_type == 'condition':
        if not node_data.get('icd_code'):
            completeness['suggestions'].append("Condition missing ICD code")
        if graph.in_degree(node_id) == 0:
            completeness['issues'].append("Condition not linked to any patient")
    
    elif node_type == 'medication':
        if not node_data.get('dosage'):
            completeness['suggestions'].append("Medication missing dosage information")
        if graph.in_degree(node_id) == 0:
            completeness['issues'].append("Medication not linked to any patient")
    
    elif node_type == 'research_article':
        if not node_data.get('authors'):
            completeness['suggestions'].append("Research article missing authors")
        if not node_data.get('url'):
            completeness['suggestions'].append("Research article missing URL")
        if graph.out_degree(node_id) == 0:
            completeness['issues'].append("Research article not linked to any conditions")
    
    completeness['is_complete'] = len(completeness['issues']) == 0
    
    return json.dumps(completeness, indent=2)


def bulk_check_node_completeness(
    node_ids: Optional[list[str]] = None,
    node_type_filter: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Check completeness for multiple nodes at once.
    
    This is much more efficient than calling check_node_completeness repeatedly.
    If no node_ids are provided, checks all nodes (optionally filtered by type).
    
    Args:
        node_ids: Optional list of specific node IDs to check. If None, checks all nodes.
        node_type_filter: Optional filter to check only nodes of specific type (e.g., 'condition', 'medication')
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with completeness analysis for all checked nodes
        
    Example:
        # Check specific nodes
        bulk_check_node_completeness(node_ids=['condition_diabetes', 'medication_metformin'])
        
        # Check all condition nodes
        bulk_check_node_completeness(node_type_filter='condition')
        
        # Check all nodes
        bulk_check_node_completeness()
    """
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized."
    
    # Determine which nodes to check
    if node_ids is not None:
        nodes_to_check = node_ids
    elif node_type_filter is not None:
        nodes_to_check = [n for n in graph.nodes() if graph.nodes[n].get('node_type') == node_type_filter]
    else:
        nodes_to_check = list(graph.nodes())
    
    # Check each node
    results = []
    summary_stats = {
        'total_checked': 0,
        'complete_nodes': 0,
        'nodes_with_issues': 0,
        'nodes_with_suggestions': 0,
        'issues_by_type': {},
        'suggestions_by_type': {}
    }
    
    for node_id in nodes_to_check:
        if node_id not in graph:
            results.append({
                'node_id': node_id,
                'error': f"Node '{node_id}' not found in graph"
            })
            continue
        
        node_data = graph.nodes[node_id]
        node_type = node_data.get('node_type', 'unknown')
        
        node_result = {
            'node_id': node_id,
            'node_type': node_type,
            'label': node_data.get('label'),
            'has_label': bool(node_data.get('label')),
            'property_count': len(node_data),
            'incoming_edges': graph.in_degree(node_id),
            'outgoing_edges': graph.out_degree(node_id),
            'issues': [],
            'suggestions': []
        }
        
        # Type-specific validation
        if node_type == 'patient':
            if not node_data.get('name'):
                node_result['issues'].append("Patient node missing 'name' property")
            if graph.out_degree(node_id) == 0:
                node_result['suggestions'].append("Patient has no conditions or medications linked")
        
        elif node_type == 'condition':
            if not node_data.get('icd_code'):
                node_result['suggestions'].append("Condition missing ICD code")
            if graph.in_degree(node_id) == 0:
                node_result['issues'].append("Condition not linked to any patient")
        
        elif node_type == 'medication':
            if not node_data.get('dosage'):
                node_result['suggestions'].append("Medication missing dosage information")
            if graph.in_degree(node_id) == 0:
                node_result['issues'].append("Medication not linked to any patient")
        
        elif node_type == 'research_article':
            if not node_data.get('authors'):
                node_result['suggestions'].append("Research article missing authors")
            if not node_data.get('url'):
                node_result['suggestions'].append("Research article missing URL")
            if graph.out_degree(node_id) == 0:
                node_result['issues'].append("Research article not linked to any conditions")
        
        elif node_type == 'clinical_trial':
            if not node_data.get('phase'):
                node_result['suggestions'].append("Clinical trial missing phase information")
            if not node_data.get('status'):
                node_result['suggestions'].append("Clinical trial missing status")
            if graph.out_degree(node_id) == 0:
                node_result['suggestions'].append("Clinical trial not linked to any conditions")
        
        node_result['is_complete'] = len(node_result['issues']) == 0
        results.append(node_result)
        
        # Update summary stats
        summary_stats['total_checked'] += 1
        if node_result['is_complete']:
            summary_stats['complete_nodes'] += 1
        if node_result['issues']:
            summary_stats['nodes_with_issues'] += 1
            summary_stats['issues_by_type'][node_type] = summary_stats['issues_by_type'].get(node_type, 0) + 1
        if node_result['suggestions']:
            summary_stats['nodes_with_suggestions'] += 1
            summary_stats['suggestions_by_type'][node_type] = summary_stats['suggestions_by_type'].get(node_type, 0) + 1
    
    # Build result
    output = {
        'summary': summary_stats,
        'nodes': results
    }
    
    return json.dumps(output, indent=2)


def analyze_graph_connectivity(tool_context: ToolContext = None) -> str:
    """Analyze the connectivity patterns in the knowledge graph.
    
    Args:
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with connectivity metrics and insights
    """
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized."
    
    # Find patient node
    patient_nodes = [n for n in graph.nodes() if graph.nodes[n].get('node_type') == 'patient']
    if not patient_nodes:
        return json.dumps({'error': 'No patient node found'}, indent=2)
    
    patient_id = patient_nodes[0]
    
    # Analyze patient's direct connections
    direct_neighbors = list(graph.neighbors(patient_id))
    neighbor_types = {}
    for neighbor in direct_neighbors:
        ntype = graph.nodes[neighbor].get('node_type', 'unknown')
        neighbor_types[ntype] = neighbor_types.get(ntype, 0) + 1
    
    # Find all nodes reachable from patient (research depth)
    reachable = nx.descendants(graph, patient_id)
    research_depth = {
        'conditions': [],
        'research_articles': [],
        'clinical_trials': []
    }
    
    for node_id in reachable:
        ntype = graph.nodes[node_id].get('node_type')
        if ntype == 'condition':
            research_depth['conditions'].append(node_id)
        elif ntype == 'research_article':
            research_depth['research_articles'].append(node_id)
        elif ntype == 'clinical_trial':
            research_depth['clinical_trials'].append(node_id)
    
    # Calculate average path length from patient to research
    research_nodes = research_depth['research_articles'] + research_depth['clinical_trials']
    path_lengths = []
    for research_node in research_nodes:
        try:
            path_length = nx.shortest_path_length(graph, patient_id, research_node)
            path_lengths.append(path_length)
        except nx.NetworkXNoPath:
            pass
    
    avg_path_length = sum(path_lengths) / len(path_lengths) if path_lengths else 0
    
    connectivity = {
        'patient_id': patient_id,
        'direct_connections': len(direct_neighbors),
        'connections_by_type': neighbor_types,
        'total_reachable_nodes': len(reachable),
        'conditions_count': len(research_depth['conditions']),
        'research_articles_count': len(research_depth['research_articles']),
        'clinical_trials_count': len(research_depth['clinical_trials']),
        'average_research_depth': round(avg_path_length, 2),
        'insights': []
    }
    
    # Generate insights
    if connectivity['conditions_count'] == 0:
        connectivity['insights'].append("No medical conditions linked to patient yet")
    
    if connectivity['research_articles_count'] == 0:
        connectivity['insights'].append("No research articles added to knowledge graph yet")
    
    if connectivity['conditions_count'] > 0 and connectivity['research_articles_count'] == 0:
        connectivity['insights'].append("Patient has conditions but no related research linked")
    
    if avg_path_length > 3:
        connectivity['insights'].append(f"Research is {avg_path_length} steps away from patient - consider more direct links")
    
    return json.dumps(connectivity, indent=2)


def list_all_nodes_by_type(node_type: str, tool_context: ToolContext = None) -> str:
    """List all nodes of a specific type in the knowledge graph.
    
    Args:
        node_type: Type of nodes to list (e.g., 'condition', 'medication', 'research_article')
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with list of nodes
    """
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized."
    
    nodes = []
    for node_id in graph.nodes():
        if graph.nodes[node_id].get('node_type') == node_type:
            node_data = graph.nodes[node_id]
            nodes.append({
                'id': node_id,
                'label': node_data.get('label'),
                'properties': {k: v for k, v in node_data.items() 
                             if k not in ['node_type', 'label']}
            })
    
    result = {
        'node_type': node_type,
        'count': len(nodes),
        'nodes': nodes
    }
    
    return json.dumps(result, indent=2)


def get_node_relationships(node_id: str, tool_context: ToolContext = None) -> str:
    """Get all relationships for a specific node.
    
    Args:
        node_id: ID of the node
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with incoming and outgoing relationships
    """
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized."
    
    if node_id not in graph:
        return f"Error: Node '{node_id}' not found in knowledge graph."
    
    # Get incoming relationships
    incoming = []
    for predecessor in graph.predecessors(node_id):
        edge_data = graph.get_edge_data(predecessor, node_id)
        pred_data = graph.nodes[predecessor]
        incoming.append({
            'from_id': predecessor,
            'from_label': pred_data.get('label'),
            'from_type': pred_data.get('node_type'),
            'relationship': edge_data.get('relationship_type'),
            'properties': {k: v for k, v in edge_data.items() 
                         if k != 'relationship_type'}
        })
    
    # Get outgoing relationships
    outgoing = []
    for successor in graph.neighbors(node_id):
        edge_data = graph.get_edge_data(node_id, successor)
        succ_data = graph.nodes[successor]
        outgoing.append({
            'to_id': successor,
            'to_label': succ_data.get('label'),
            'to_type': succ_data.get('node_type'),
            'relationship': edge_data.get('relationship_type'),
            'properties': {k: v for k, v in edge_data.items() 
                         if k != 'relationship_type'}
        })
    
    node_data = graph.nodes[node_id]
    result = {
        'node_id': node_id,
        'node_label': node_data.get('label'),
        'node_type': node_data.get('node_type'),
        'incoming_relationships': incoming,
        'outgoing_relationships': outgoing,
        'total_incoming': len(incoming),
        'total_outgoing': len(outgoing)
    }
    
    return json.dumps(result, indent=2)


# Graph persistence tools

def save_graph_to_disk(
    filename: str,
    output_dir: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Save the knowledge graph to disk in multiple formats for review.
    
    Args:
        filename: Base filename without extension (e.g., 'patient_123_kg')
        output_dir: Optional directory path. Defaults to project root 'knowledge_graphs/' directory
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message with file paths
    """
    from pathlib import Path
    import datetime
    
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized. Nothing to save."
    
    # Set default output directory to project root
    if output_dir is None:
        # Find project root (where pyproject.toml is located)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent  # tools -> patientmap -> src -> project_root
        output_dir = project_root / "knowledge_graphs"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Add timestamp to filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{filename}_{timestamp}"
    
    saved_files = []
    
    # 1. Save as JSON (node-link format) - easiest to read
    json_path = output_dir / f"{base_name}.json"
    data = nx.node_link_data(graph)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    saved_files.append(str(json_path))
    
    # 2. Save as GraphML (XML format) - good for visualization tools
    # GraphML doesn't support list/dict types, so create a clean version
    graphml_path = output_dir / f"{base_name}.graphml"
    try:
        # Create a new graph with stringified complex attributes
        graph_for_graphml = nx.DiGraph()
        
        # Copy nodes with stringified attributes
        for node_id in graph.nodes():
            node_attrs = {}
            for key, value in graph.nodes[node_id].items():
                if isinstance(value, (list, dict)):
                    node_attrs[key] = json.dumps(value)
                else:
                    node_attrs[key] = str(value) if value is not None else ""
            graph_for_graphml.add_node(node_id, **node_attrs)
        
        # Copy edges with stringified attributes
        for source, target in graph.edges():
            edge_attrs = {}
            edge_data = graph.get_edge_data(source, target)
            for key, value in edge_data.items():
                if isinstance(value, (list, dict)):
                    edge_attrs[key] = json.dumps(value)
                else:
                    edge_attrs[key] = str(value) if value is not None else ""
            graph_for_graphml.add_edge(source, target, **edge_attrs)
        
        nx.write_graphml(graph_for_graphml, graphml_path)
        saved_files.append(str(graphml_path))
    except Exception as e:
        # If GraphML export fails, just skip it and continue with other formats
        saved_files.append(f"GraphML export skipped: {str(e)}")
    
    # 3. Save human-readable summary
    summary_path = output_dir / f"{base_name}_summary.txt"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("Knowledge Graph Summary\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*80}\n\n")
        
        # Patient info
        patient_nodes = [n for n in graph.nodes() if graph.nodes[n].get('node_type') == 'patient']
        if patient_nodes:
            patient_id = patient_nodes[0]
            patient_data = graph.nodes[patient_id]
            f.write(f"PATIENT: {patient_data.get('name', patient_id)}\n")
            f.write(f"ID: {patient_id}\n\n")
        
        # Statistics
        f.write("STATISTICS:\n")
        f.write(f"  Total Nodes: {graph.number_of_nodes()}\n")
        f.write(f"  Total Edges: {graph.number_of_edges()}\n\n")
        
        # Nodes by type
        node_types = {}
        for node_id in graph.nodes():
            ntype = graph.nodes[node_id].get('node_type', 'unknown')
            node_types[ntype] = node_types.get(ntype, 0) + 1
        
        f.write("NODES BY TYPE:\n")
        for ntype, count in sorted(node_types.items()):
            f.write(f"  {ntype}: {count}\n")
        f.write("\n")
        
        # List all nodes with details
        f.write("ALL NODES:\n")
        f.write(f"{'-'*80}\n")
        for node_id in sorted(graph.nodes()):
            node_data = graph.nodes[node_id]
            f.write(f"\n[{node_data.get('node_type', 'unknown').upper()}] {node_data.get('label', node_id)}\n")
            f.write(f"  ID: {node_id}\n")
            for key, value in node_data.items():
                if key not in ['node_type', 'label']:
                    f.write(f"  {key}: {value}\n")
            
            # Show relationships
            in_edges = list(graph.in_edges(node_id, data=True))
            out_edges = list(graph.out_edges(node_id, data=True))
            
            if in_edges:
                f.write("  Incoming relationships:\n")
                for src, _, edge_data in in_edges:
                    src_label = graph.nodes[src].get('label', src)
                    rel_type = edge_data.get('relationship_type', 'UNKNOWN')
                    f.write(f"    <- {src_label} [{rel_type}]\n")
            
            if out_edges:
                f.write("  Outgoing relationships:\n")
                for _, tgt, edge_data in out_edges:
                    tgt_label = graph.nodes[tgt].get('label', tgt)
                    rel_type = edge_data.get('relationship_type', 'UNKNOWN')
                    f.write(f"    -> {tgt_label} [{rel_type}]\n")
        
        f.write(f"\n{'-'*80}\n")
        f.write("End of Knowledge Graph Summary\n")
    
    saved_files.append(str(summary_path))
    
    result = {
        'status': 'success',
        'files_saved': saved_files,
        'output_directory': str(output_dir),
        'node_count': graph.number_of_nodes(),
        'edge_count': graph.number_of_edges()
    }
    
    return json.dumps(result, indent=2)


def load_graph_from_disk(
    filepath: str,
    tool_context: ToolContext = None
) -> str:
    """Load a knowledge graph from disk (JSON or GraphML format).
    
    Args:
        filepath: Path to the graph file (.json or .graphml)
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message with graph statistics
    """
    from pathlib import Path
    
    path = Path(filepath)
    
    if not path.exists():
        return f"Error: File not found: {filepath}"
    
    try:
        if path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            graph = nx.node_link_graph(data, directed=True)
        elif path.suffix == '.graphml':
            graph = nx.read_graphml(path)
        else:
            return "Error: Unsupported file format. Use .json or .graphml files."
        
        _save_graph(graph, tool_context)
        
        result = {
            'status': 'success',
            'loaded_from': str(filepath),
            'node_count': graph.number_of_nodes(),
            'edge_count': graph.number_of_edges()
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Error loading graph: {str(e)}"


def export_graph_as_cytoscape_json(
    filename: str,
    output_dir: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Export graph in Cytoscape.js JSON format for web visualization.
    
    Args:
        filename: Output filename without extension
        output_dir: Optional directory path. Defaults to project root 'knowledge_graphs/' directory
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message with file path
    """
    from pathlib import Path
    import datetime
    
    graph = _get_graph(tool_context)
    
    if graph.number_of_nodes() == 0:
        return "Error: Knowledge graph not initialized. Nothing to export."
    
    if output_dir is None:
        # Find project root (where pyproject.toml is located)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent  # tools -> patientmap -> src -> project_root
        output_dir = project_root / "knowledge_graphs"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{filename}_{timestamp}_cytoscape.json"
    
    # Convert to Cytoscape format
    cytoscape_data = {
        "elements": {
            "nodes": [],
            "edges": []
        }
    }
    
    # Add nodes
    for node_id in graph.nodes():
        node_data = graph.nodes[node_id]
        cytoscape_node = {
            "data": {
                "id": node_id,
                "label": node_data.get('label', node_id),
                "type": node_data.get('node_type', 'unknown'),
                **{k: v for k, v in node_data.items() if k not in ['label', 'node_type']}
            }
        }
        cytoscape_data["elements"]["nodes"].append(cytoscape_node)
    
    # Add edges
    for i, (source, target) in enumerate(graph.edges()):
        edge_data = graph.get_edge_data(source, target)
        cytoscape_edge = {
            "data": {
                "id": f"edge_{i}",
                "source": source,
                "target": target,
                "label": edge_data.get('relationship_type', ''),
                **{k: v for k, v in edge_data.items() if k != 'relationship_type'}
            }
        }
        cytoscape_data["elements"]["edges"].append(cytoscape_edge)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cytoscape_data, f, indent=2)
    
    result = {
        'status': 'success',
        'file_saved': str(output_path),
        'format': 'Cytoscape.js JSON',
        'node_count': len(cytoscape_data["elements"]["nodes"]),
        'edge_count': len(cytoscape_data["elements"]["edges"])
    }
    
    return json.dumps(result, indent=2)


# Node and relationship deletion tools

def delete_node(
    node_id: str,
    tool_context: ToolContext
) -> str:
    """Delete a node from the knowledge graph.
    
    This will also remove all edges connected to this node.
    
    Args:
        node_id: ID of the node to delete
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with deletion status
    """
    graph = _get_graph(tool_context)
    
    if not graph.has_node(node_id):
        return json.dumps({
            'status': 'error',
            'message': f"Node '{node_id}' does not exist in the graph"
        }, indent=2)
    
    # Get node info before deletion for reporting
    node_data = dict(graph.nodes[node_id])
    in_edges = list(graph.in_edges(node_id))
    out_edges = list(graph.out_edges(node_id))
    total_edges = len(in_edges) + len(out_edges)
    
    # Remove the node (automatically removes connected edges)
    graph.remove_node(node_id)
    
    _save_graph(graph, tool_context)
    
    result = {
        'status': 'success',
        'deleted_node': node_id,
        'node_type': node_data.get('node_type', 'unknown'),
        'node_label': node_data.get('label', node_id),
        'edges_removed': total_edges,
        'message': f"Successfully deleted node '{node_id}' and {total_edges} connected edges"
    }
    
    return json.dumps(result, indent=2)


def delete_relationship(
    source_node: str,
    target_node: str,
    tool_context: ToolContext
) -> str:
    """Delete a relationship (edge) between two nodes.
    
    Args:
        source_node: ID of the source node
        target_node: ID of the target node
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with deletion status
    """
    graph = _get_graph(tool_context)
    
    if not graph.has_node(source_node):
        return json.dumps({
            'status': 'error',
            'message': f"Source node '{source_node}' does not exist"
        }, indent=2)
    
    if not graph.has_node(target_node):
        return json.dumps({
            'status': 'error',
            'message': f"Target node '{target_node}' does not exist"
        }, indent=2)
    
    if not graph.has_edge(source_node, target_node):
        return json.dumps({
            'status': 'error',
            'message': f"No edge exists from '{source_node}' to '{target_node}'"
        }, indent=2)
    
    # Get edge info before deletion
    edge_data = graph.get_edge_data(source_node, target_node)
    relationship_type = edge_data.get('relationship_type', 'unknown')
    
    # Remove the edge
    graph.remove_edge(source_node, target_node)
    
    _save_graph(graph, tool_context)
    
    result = {
        'status': 'success',
        'deleted_edge': {
            'source': source_node,
            'target': target_node,
            'relationship_type': relationship_type
        },
        'message': f"Successfully deleted '{relationship_type}' relationship from '{source_node}' to '{target_node}'"
    }
    
    return json.dumps(result, indent=2)


def merge_duplicate_nodes(
    primary_node_id: str,
    duplicate_node_id: str,
    tool_context: ToolContext
) -> str:
    """Merge a duplicate node into a primary node, transferring all relationships.
    
    This will:
    1. Transfer all incoming edges from duplicate to primary
    2. Transfer all outgoing edges from duplicate to primary
    3. Merge node attributes (primary takes precedence, but missing attrs are copied)
    4. Delete the duplicate node
    
    Args:
        primary_node_id: ID of the node to keep
        duplicate_node_id: ID of the duplicate node to merge and delete
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with merge status
    """
    graph = _get_graph(tool_context)
    
    if not graph.has_node(primary_node_id):
        return json.dumps({
            'status': 'error',
            'message': f"Primary node '{primary_node_id}' does not exist"
        }, indent=2)
    
    if not graph.has_node(duplicate_node_id):
        return json.dumps({
            'status': 'error',
            'message': f"Duplicate node '{duplicate_node_id}' does not exist"
        }, indent=2)
    
    if primary_node_id == duplicate_node_id:
        return json.dumps({
            'status': 'error',
            'message': "Primary and duplicate node IDs must be different"
        }, indent=2)
    
    # Get node data
    primary_data = dict(graph.nodes[primary_node_id])
    duplicate_data = dict(graph.nodes[duplicate_node_id])
    
    # Merge attributes (primary takes precedence, fill in missing)
    for key, value in duplicate_data.items():
        if key not in primary_data or primary_data[key] is None:
            primary_data[key] = value
    
    # Update primary node with merged attributes
    graph.nodes[primary_node_id].update(primary_data)
    
    # Transfer all incoming edges to duplicate node
    edges_transferred = 0
    for source, _ in list(graph.in_edges(duplicate_node_id)):
        if source != primary_node_id:  # Avoid self-loop
            edge_data = graph.get_edge_data(source, duplicate_node_id)
            if not graph.has_edge(source, primary_node_id):
                graph.add_edge(source, primary_node_id, **edge_data)
                edges_transferred += 1
    
    # Transfer all outgoing edges from duplicate node
    for _, target in list(graph.out_edges(duplicate_node_id)):
        if target != primary_node_id:  # Avoid self-loop
            edge_data = graph.get_edge_data(duplicate_node_id, target)
            if not graph.has_edge(primary_node_id, target):
                graph.add_edge(primary_node_id, target, **edge_data)
                edges_transferred += 1
    
    # Delete the duplicate node
    graph.remove_node(duplicate_node_id)
    
    _save_graph(graph, tool_context)
    
    result = {
        'status': 'success',
        'primary_node': primary_node_id,
        'merged_node': duplicate_node_id,
        'edges_transferred': edges_transferred,
        'merged_attributes': list(duplicate_data.keys()),
        'message': f"Successfully merged '{duplicate_node_id}' into '{primary_node_id}' and transferred {edges_transferred} relationships"
    }
    
    return json.dumps(result, indent=2)


def list_knowledge_graphs(
    directory: Optional[str] = None,
    pattern: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """List available knowledge graph files in the knowledge_graphs directory.
    
    Args:
        directory: Optional directory path. Defaults to 'src/knowledge_graphs/'
        pattern: Optional filename pattern to filter (e.g., 'Marcus_Williams', 'validated_kg')
        tool_context: ADK tool context (not used, for consistency)
        
    Returns:
        JSON list of available graph files with metadata
    """
    from pathlib import Path
    import datetime
    
    if directory is None:
        # Find project root and default to knowledge_graphs directory
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        directory = project_root / "knowledge_graphs"
    else:
        directory = Path(directory)
    
    if not directory.exists():
        return json.dumps({
            'status': 'error',
            'message': f"Directory not found: {directory}",
            'graphs': []
        }, indent=2)
    
    # Find all JSON and GraphML files
    graph_files = []
    
    for ext in ['*.json', '*.graphml']:
        for filepath in directory.glob(ext):
            # Skip cytoscape export files
            if '_cytoscape.json' in filepath.name:
                continue
                
            # Apply pattern filter if specified
            if pattern and pattern.lower() not in filepath.name.lower():
                continue
            
            stat = filepath.stat()
            modified_time = datetime.datetime.fromtimestamp(stat.st_mtime)
            
            graph_files.append({
                'filename': filepath.name,
                'filepath': str(filepath),
                'size_kb': round(stat.st_size / 1024, 2),
                'modified': modified_time.strftime("%Y-%m-%d %H:%M:%S"),
                'format': filepath.suffix[1:]  # Remove the dot
            })
    
    # Sort by modified time (most recent first)
    graph_files.sort(key=lambda x: x['modified'], reverse=True)
    
    result = {
        'status': 'success',
        'directory': str(directory),
        'pattern_filter': pattern if pattern else 'none',
        'count': len(graph_files),
        'graphs': graph_files
    }
    
    if graph_files:
        result['most_recent'] = graph_files[0]['filepath']
    
    return json.dumps(result, indent=2)
