"""
Neo4j Knowledge Graph Tools for PatientMap Agents

This module provides tools for creating, manipulating, and querying knowledge graphs
using Neo4j Aura. These tools work alongside the NetworkX tools, providing persistent
graph storage in a production-grade graph database.

Usage Pattern:
1. NetworkX tools remain for in-memory operations during research phase
2. Neo4j tools provide persistent storage and advanced graph queries
3. Both toolsets can coexist - use NetworkX for prototyping, Neo4j for production
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Optional, Any
from google.adk.tools.tool_context import ToolContext
import json

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from patientmap.common.neo4j_client import Neo4jClient, initialize_neo4j_constraints


# Connection Management

def verify_neo4j_connection(tool_context: ToolContext) -> str:
    """Verify Neo4j connection and return database information.
    
    Args:
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with connection status and server info
    """
    info = Neo4jClient.verify_connection(tool_context)
    return json.dumps(info, indent=2)


def initialize_neo4j_schema(tool_context: ToolContext) -> str:
    """Initialize Neo4j database constraints and indexes.
    
    Should be called once at the beginning of a session to ensure
    proper schema constraints are in place.
    
    Args:
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message
    """
    return initialize_neo4j_constraints(tool_context)


# Graph Initialization

def neo4j_initialize_patient_graph(
    patient_id: str,
    patient_name: str,
    tool_context: ToolContext
) -> str:
    """Initialize a new knowledge graph for a patient in Neo4j.
    
    Creates a Patient node with unique patient_id constraint.
    
    Args:
        patient_id: Unique identifier for the patient
        patient_name: Name of the patient
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message with patient node details
    """
    with Neo4jClient.get_session(tool_context) as session:
        result = session.run("""
            MERGE (p:Patient {patient_id: $patient_id})
            SET p.name = $patient_name,
                p.created_at = datetime(),
                p.updated_at = datetime()
            RETURN p
        """, patient_id=patient_id, patient_name=patient_name)
        
        record = result.single()
        if record:
            return f"Initialized Neo4j knowledge graph with Patient node: {patient_id} ({patient_name})"
        else:
            return f"Error: Failed to create patient node in Neo4j"


# Node Operations

def neo4j_add_condition(
    patient_id: str,
    condition_id: str,
    condition_name: str,
    icd_code: Optional[str] = None,
    symptoms: Optional[list[str]] = None,
    tool_context: ToolContext = None
) -> str:
    """Add a medical condition to the patient's Neo4j knowledge graph.
    
    Args:
        patient_id: ID of the patient node
        condition_id: Unique identifier for the condition
        condition_name: Name of the medical condition
        icd_code: Optional ICD code for the condition
        symptoms: Optional list of symptoms
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message
    """
    with Neo4jClient.get_session(tool_context) as session:
        # Create condition node
        query = """
            MERGE (c:Condition {condition_id: $condition_id})
            SET c.label = $condition_name,
                c.name = $condition_name,
                c.icd_code = $icd_code,
                c.symptoms = $symptoms,
                c.created_at = datetime(),
                c.updated_at = datetime()
            WITH c
            MATCH (p:Patient {patient_id: $patient_id})
            MERGE (p)-[r:HAS_CONDITION]->(c)
            SET r.created_at = datetime()
            RETURN c, p, r
        """
        
        result = session.run(
            query,
            patient_id=patient_id,
            condition_id=condition_id,
            condition_name=condition_name,
            icd_code=icd_code,
            symptoms=symptoms
        )
        
        record = result.single()
        if record:
            return f"Added Condition: {condition_name} (ID: {condition_id}) to patient {patient_id} in Neo4j"
        else:
            return f"Error: Failed to add condition or link to patient"


def neo4j_add_medication(
    patient_id: str,
    medication_id: str,
    medication_name: str,
    dosage: Optional[str] = None,
    frequency: Optional[str] = None,
    side_effects: Optional[list[str]] = None,
    tool_context: ToolContext = None
) -> str:
    """Add a medication to the patient's Neo4j knowledge graph.
    
    Args:
        patient_id: ID of the patient node
        medication_id: Unique identifier for the medication
        medication_name: Name of the medication
        dosage: Optional dosage information
        frequency: Optional frequency (e.g., 'BID', 'QD')
        side_effects: Optional list of side effects
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = """
            MERGE (m:Medication {medication_id: $medication_id})
            SET m.label = $medication_name,
                m.name = $medication_name,
                m.dosage = $dosage,
                m.frequency = $frequency,
                m.side_effects = $side_effects,
                m.created_at = datetime(),
                m.updated_at = datetime()
            WITH m
            MATCH (p:Patient {patient_id: $patient_id})
            MERGE (p)-[r:TAKES_MEDICATION]->(m)
            SET r.created_at = datetime()
            RETURN m, p, r
        """
        
        result = session.run(
            query,
            patient_id=patient_id,
            medication_id=medication_id,
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            side_effects=side_effects
        )
        
        record = result.single()
        if record:
            return f"Added Medication: {medication_name} (ID: {medication_id}) to patient {patient_id} in Neo4j"
        else:
            return f"Error: Failed to add medication or link to patient"


def neo4j_bulk_add_conditions(
    patient_id: str,
    conditions: list[dict],
    tool_context: ToolContext = None
) -> str:
    """Add multiple conditions to a patient in Neo4j efficiently.
    
    Uses Cypher UNWIND for batch processing.
    
    Args:
        patient_id: ID of the patient
        conditions: List of condition dictionaries, each containing:
            - condition_id (str): Unique identifier
            - condition_name (str): Name of the condition
            - icd_code (str): ICD code
            - symptoms (str, optional): Description of symptoms
        tool_context: ADK tool context
        
    Returns:
        Success message with count
        
    Example:
        neo4j_bulk_add_conditions(
            patient_id="P001",
            conditions=[
                {"condition_id": "C001", "condition_name": "Hypertension", "icd_code": "I10", "symptoms": "elevated BP"},
                {"condition_id": "C002", "condition_name": "Type 2 Diabetes", "icd_code": "E11.9", "symptoms": "elevated glucose"}
            ]
        )
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = """
            MATCH (p:Patient {patient_id: $patient_id})
            UNWIND $conditions AS cond
            MERGE (c:Condition {condition_id: cond.condition_id})
            SET c.label = cond.condition_name,
                c.name = cond.condition_name,
                c.icd_code = cond.icd_code,
                c.symptoms = cond.symptoms,
                c.created_at = datetime(),
                c.updated_at = datetime()
            MERGE (p)-[r:HAS_CONDITION]->(c)
            SET r.created_at = datetime()
            RETURN count(c) AS condition_count
        """
        
        result = session.run(query, patient_id=patient_id, conditions=conditions)
        record = result.single()
        
        if record:
            return f"Added {record['condition_count']} conditions to patient {patient_id} in Neo4j"
        else:
            return "Error: Failed to add conditions"


def neo4j_bulk_add_medications(
    patient_id: str,
    medications: list[dict],
    tool_context: ToolContext = None
) -> str:
    """Add multiple medications to a patient in Neo4j efficiently.
    
    Uses Cypher UNWIND for batch processing.
    
    Args:
        patient_id: ID of the patient
        medications: List of medication dictionaries, each containing:
            - medication_id (str): Unique identifier
            - medication_name (str): Name of the medication
            - dosage (str): Dosage information
            - frequency (str): How often taken
            - side_effects (str, optional): Side effects
        tool_context: ADK tool context
        
    Returns:
        Success message with count
        
    Example:
        neo4j_bulk_add_medications(
            patient_id="P001",
            medications=[
                {"medication_id": "M001", "medication_name": "Lisinopril", "dosage": "5mg", "frequency": "daily", "side_effects": ""},
                {"medication_id": "M002", "medication_name": "Metformin", "dosage": "500mg", "frequency": "twice daily", "side_effects": ""}
            ]
        )
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = """
            MATCH (p:Patient {patient_id: $patient_id})
            UNWIND $medications AS med
            MERGE (m:Medication {medication_id: med.medication_id})
            SET m.label = med.medication_name,
                m.name = med.medication_name,
                m.dosage = med.dosage,
                m.frequency = med.frequency,
                m.side_effects = med.side_effects,
                m.created_at = datetime(),
                m.updated_at = datetime()
            MERGE (p)-[r:TAKES_MEDICATION]->(m)
            SET r.created_at = datetime()
            RETURN count(m) AS medication_count
        """
        
        result = session.run(query, patient_id=patient_id, medications=medications)
        record = result.single()
        
        if record:
            return f"Added {record['medication_count']} medications to patient {patient_id} in Neo4j"
        else:
            return "Error: Failed to add medications"


def neo4j_add_research_article(
    article_id: str,
    article_title: str,
    authors: Optional[list[str]] = None,
    publication_date: Optional[str] = None,
    journal: Optional[str] = None,
    url: Optional[str] = None,
    abstract: Optional[str] = None,
    keywords: Optional[list[str]] = None,
    tool_context: ToolContext = None
) -> str:
    """Add a research article to the Neo4j knowledge graph.
    
    Args:
        article_id: Unique identifier for the article
        article_title: Title of the research article
        authors: Optional list of authors
        publication_date: Optional publication date
        journal: Optional journal name
        url: Optional URL to the article
        abstract: Optional abstract text
        keywords: Optional list of keywords
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = """
            MERGE (a:ResearchArticle {article_id: $article_id})
            SET a.title = $article_title,
                a.label = $article_title,
                a.authors = $authors,
                a.publication_date = $publication_date,
                a.journal = $journal,
                a.url = $url,
                a.abstract = $abstract,
                a.keywords = $keywords,
                a.created_at = datetime(),
                a.updated_at = datetime()
            RETURN a
        """
        
        result = session.run(
            query,
            article_id=article_id,
            article_title=article_title,
            authors=authors,
            publication_date=publication_date,
            journal=journal,
            url=url,
            abstract=abstract,
            keywords=keywords
        )
        
        record = result.single()
        if record:
            return f"Added ResearchArticle: {article_title} (ID: {article_id}) to Neo4j"
        else:
            return f"Error: Failed to add research article"


def neo4j_add_clinical_trial(
    trial_id: str,
    trial_title: str,
    phase: Optional[str] = None,
    status: Optional[str] = None,
    conditions: Optional[list[str]] = None,
    interventions: Optional[list[str]] = None,
    url: Optional[str] = None,
    enrollment: Optional[int] = None,
    start_date: Optional[str] = None,
    completion_date: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Add a clinical trial to the Neo4j knowledge graph.
    
    Args:
        trial_id: Clinical trial identifier (e.g., NCT number)
        trial_title: Title of the clinical trial
        phase: Optional trial phase (e.g., 'Phase 3')
        status: Optional trial status (e.g., 'Recruiting', 'Completed')
        conditions: Optional list of conditions being studied
        interventions: Optional list of interventions being tested
        url: Optional URL to trial details
        enrollment: Optional number of participants
        start_date: Optional start date
        completion_date: Optional completion date
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = """
            MERGE (t:ClinicalTrial {trial_id: $trial_id})
            SET t.title = $trial_title,
                t.label = $trial_title,
                t.phase = $phase,
                t.status = $status,
                t.conditions = $conditions,
                t.interventions = $interventions,
                t.url = $url,
                t.enrollment = $enrollment,
                t.start_date = $start_date,
                t.completion_date = $completion_date,
                t.created_at = datetime(),
                t.updated_at = datetime()
            RETURN t
        """
        
        result = session.run(
            query,
            trial_id=trial_id,
            trial_title=trial_title,
            phase=phase,
            status=status,
            conditions=conditions,
            interventions=interventions,
            url=url,
            enrollment=enrollment,
            start_date=start_date,
            completion_date=completion_date
        )
        
        record = result.single()
        if record:
            return f"Added ClinicalTrial: {trial_title} (ID: {trial_id}) to Neo4j"
        else:
            return f"Error: Failed to add clinical trial"


def neo4j_link_article_to_condition(
    article_id: str,
    condition_id: str,
    relevance: str = "related",
    confidence: Optional[float] = None,
    tool_context: ToolContext = None
) -> str:
    """Link a research article to a medical condition in Neo4j.
    
    Args:
        article_id: ID of the research article node
        condition_id: ID of the condition node
        relevance: Type of relevance ('related', 'treatment', 'diagnosis', 'prognosis')
        confidence: Optional confidence score (0.0 to 1.0)
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = """
            MATCH (a:ResearchArticle {article_id: $article_id})
            MATCH (c:Condition {condition_id: $condition_id})
            MERGE (a)-[r:STUDIES]->(c)
            SET r.relevance = $relevance,
                r.confidence = $confidence,
                r.created_at = datetime()
            RETURN a, c, r
        """
        
        result = session.run(
            query,
            article_id=article_id,
            condition_id=condition_id,
            relevance=relevance,
            confidence=confidence
        )
        
        record = result.single()
        if record:
            return f"Linked article {article_id} to condition {condition_id} with relevance '{relevance}'"
        else:
            return f"Error: Failed to link article to condition (check IDs exist)"


def neo4j_bulk_link_articles_to_conditions(
    links: list[dict[str, Any]],
    tool_context: ToolContext = None
) -> str:
    """Link multiple research articles to conditions in Neo4j efficiently.
    
    Uses Cypher UNWIND for batch processing.
    
    Args:
        links: List of link dictionaries, each containing:
            - article_id (str): ID of the research article node
            - condition_id (str): ID of the condition node
            - relevance (str, optional): Type of relevance (default: 'related')
            - confidence (float, optional): Confidence score (0.0 to 1.0)
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message with count of links created
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = """
            UNWIND $links AS link
            MATCH (a:ResearchArticle {article_id: link.article_id})
            MATCH (c:Condition {condition_id: link.condition_id})
            MERGE (a)-[r:STUDIES]->(c)
            SET r.relevance = coalesce(link.relevance, 'related'),
                r.confidence = link.confidence,
                r.created_at = datetime()
            RETURN count(r) AS links_created
        """
        
        result = session.run(query, links=links)
        record = result.single()
        
        if record:
            count = record['links_created']
            return f"Successfully created {count} article-condition links in Neo4j from {len(links)} input records"
        else:
            return "Error: Failed to create links"


def neo4j_bulk_link_articles_to_medications(
    links: list[dict[str, Any]],
    tool_context: ToolContext = None
) -> str:
    """Link multiple research articles to medications in Neo4j efficiently.
    
    Uses Cypher UNWIND for batch processing. Creates INFORMS_MEDICATION_MANAGEMENT
    relationships from research articles to medication nodes.
    
    Args:
        links: List of link dictionaries, each containing:
            - article_id (str): ID of the research article node
            - medication_id (str): ID of the medication node (e.g., "M001")
            - medication_name (str, optional): Name of the medication for reference
            - relevance (str, optional): Type of relevance (e.g., 'efficacy', 'safety', 'interactions', 'dosing')
            - confidence (float, optional): Confidence score (0.0 to 1.0)
            - notes (str, optional): Additional context about the link
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message with count of links created
        
    Example:
        neo4j_bulk_link_articles_to_medications(links=[
            {
                "article_id": "RA_Topic_02",
                "medication_id": "M001",
                "medication_name": "Lisinopril",
                "relevance": "interactions",
                "confidence": 0.9,
                "notes": "Drug-drug interaction with NSAIDs"
            },
            {
                "article_id": "RA_Topic_02",
                "medication_id": "M002",
                "medication_name": "Metoprolol",
                "relevance": "safety",
                "confidence": 0.85
            }
        ])
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = """
            UNWIND $links AS link
            MATCH (a:ResearchArticle {article_id: link.article_id})
            MATCH (m:Medication {id: link.medication_id})
            MERGE (a)-[r:INFORMS_MEDICATION_MANAGEMENT]->(m)
            SET r.medication_name = link.medication_name,
                r.relevance = coalesce(link.relevance, 'general'),
                r.confidence = link.confidence,
                r.notes = link.notes,
                r.created_at = datetime()
            RETURN count(r) AS links_created
        """
        
        result = session.run(query, links=links)
        record = result.single()
        
        if record:
            count = record['links_created']
            return f"Successfully created {count} article-medication links in Neo4j from {len(links)} input records"
        else:
            return "Error: Failed to create medication links"


# Query Operations

def neo4j_get_patient_overview(
    patient_id: str,
    tool_context: ToolContext = None
) -> str:
    """Get a comprehensive overview of a patient's knowledge graph from Neo4j.
    
    Args:
        patient_id: ID of the patient node
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with patient overview
    """
    with Neo4jClient.get_session(tool_context) as session:
        # Get patient and related data
        query = """
            MATCH (p:Patient {patient_id: $patient_id})
            OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
            OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m:Medication)
            OPTIONAL MATCH (a:ResearchArticle)-[:STUDIES]->(c)
            RETURN p,
                   collect(DISTINCT c) AS conditions,
                   collect(DISTINCT m) AS medications,
                   count(DISTINCT a) AS research_count
        """
        
        result = session.run(query, patient_id=patient_id)
        record = result.single()
        
        if not record:
            return json.dumps({'error': f'Patient {patient_id} not found in Neo4j'}, indent=2)
        
        patient = dict(record['p'])
        conditions = [dict(c) for c in record['conditions'] if c]
        medications = [dict(m) for m in record['medications'] if m]
        
        overview = {
            'patient_id': patient_id,
            'patient_name': patient.get('name'),
            'conditions': [
                {
                    'id': c.get('condition_id'),
                    'name': c.get('name'),
                    'icd_code': c.get('icd_code')
                }
                for c in conditions
            ],
            'medications': [
                {
                    'id': m.get('medication_id'),
                    'name': m.get('name'),
                    'dosage': m.get('dosage')
                }
                for m in medications
            ],
            'research_articles_count': record['research_count']
        }
        
        return json.dumps(overview, indent=2)


def neo4j_find_related_research(
    condition_id: str,
    max_results: int = 10,
    tool_context: ToolContext = None
) -> str:
    """Find research articles related to a specific condition in Neo4j.
    
    Args:
        condition_id: ID of the condition node
        max_results: Maximum number of articles to return
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with list of related research articles
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = """
            MATCH (a:ResearchArticle)-[r:STUDIES]->(c:Condition {condition_id: $condition_id})
            RETURN a, r
            ORDER BY coalesce(r.confidence, 0.5) DESC
            LIMIT $max_results
        """
        
        result = session.run(query, condition_id=condition_id, max_results=max_results)
        
        articles = []
        for record in result:
            article = dict(record['a'])
            rel = dict(record['r'])
            
            articles.append({
                'id': article.get('article_id'),
                'title': article.get('title'),
                'authors': article.get('authors'),
                'journal': article.get('journal'),
                'url': article.get('url'),
                'relevance': rel.get('relevance'),
                'confidence': rel.get('confidence')
            })
        
        return json.dumps({
            'condition_id': condition_id,
            'articles': articles,
            'total_found': len(articles)
        }, indent=2)


def neo4j_export_graph_summary(tool_context: ToolContext = None) -> str:
    """Export a summary of the entire Neo4j knowledge graph.
    
    Args:
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with graph statistics
    """
    with Neo4jClient.get_session(tool_context) as session:
        # Count nodes by label
        nodes_query = """
            CALL db.labels() YIELD label
            CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN count(n) AS count', {})
            YIELD value
            RETURN label, value.count AS count
        """
        
        # Fallback query if APOC not available
        simple_query = """
            MATCH (n)
            RETURN labels(n)[0] AS label, count(n) AS count
        """
        
        try:
            result = session.run(nodes_query)
            nodes_by_type = {record['label']: record['count'] for record in result}
        except:
            # APOC not available, use simple query
            result = session.run(simple_query)
            nodes_by_type = {record['label']: record['count'] for record in result}
        
        # Count relationships by type
        rels_query = """
            MATCH ()-[r]->()
            RETURN type(r) AS rel_type, count(r) AS count
        """
        
        result = session.run(rels_query)
        edges_by_type = {record['rel_type']: record['count'] for record in result}
        
        # Total counts
        total_nodes = sum(nodes_by_type.values())
        total_edges = sum(edges_by_type.values())
        
        summary = {
            'total_nodes': total_nodes,
            'total_edges': total_edges,
            'nodes_by_type': nodes_by_type,
            'edges_by_type': edges_by_type,
            'database': 'Neo4j Aura'
        }
        
        return json.dumps(summary, indent=2)


def neo4j_analyze_graph_connectivity(
    patient_id: str,
    tool_context: ToolContext = None
) -> str:
    """Analyze connectivity patterns in the Neo4j knowledge graph.
    
    Args:
        patient_id: ID of the patient node
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with connectivity metrics
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = """
            MATCH (p:Patient {patient_id: $patient_id})
            OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
            OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m:Medication)
            OPTIONAL MATCH (a:ResearchArticle)-[:STUDIES]->(c)
            WITH p, 
                 count(DISTINCT c) AS condition_count,
                 count(DISTINCT m) AS medication_count,
                 count(DISTINCT a) AS research_count,
                 collect(DISTINCT c.condition_id) AS condition_ids
            OPTIONAL MATCH path = (p)-[*1..3]->(end)
            RETURN p, 
                   condition_count,
                   medication_count,
                   research_count,
                   count(DISTINCT end) AS reachable_nodes,
                   avg(length(path)) AS avg_path_length
        """
        
        result = session.run(query, patient_id=patient_id)
        record = result.single()
        
        if not record:
            return json.dumps({'error': f'Patient {patient_id} not found'}, indent=2)
        
        connectivity = {
            'patient_id': patient_id,
            'conditions_count': record['condition_count'],
            'medications_count': record['medication_count'],
            'research_articles_count': record['research_count'],
            'total_reachable_nodes': record['reachable_nodes'],
            'average_path_length': round(record['avg_path_length'] or 0, 2),
            'insights': []
        }
        
        # Generate insights
        if connectivity['conditions_count'] == 0:
            connectivity['insights'].append("No medical conditions linked to patient yet")
        
        if connectivity['research_articles_count'] == 0:
            connectivity['insights'].append("No research articles added to knowledge graph yet")
        
        if connectivity['conditions_count'] > 0 and connectivity['research_articles_count'] == 0:
            connectivity['insights'].append("Patient has conditions but no related research linked")
        
        return json.dumps(connectivity, indent=2)


# Graph Persistence

def neo4j_clear_patient_graph(
    patient_id: str,
    tool_context: ToolContext = None
) -> str:
    """Clear all data for a specific patient from Neo4j.
    
    WARNING: This will delete the patient node and all related nodes/relationships.
    Use with caution.
    
    Args:
        patient_id: ID of the patient node
        tool_context: ADK tool context for state management
        
    Returns:
        Confirmation message with deletion count
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = """
            MATCH (p:Patient {patient_id: $patient_id})
            OPTIONAL MATCH (p)-[r]->(related)
            DETACH DELETE p, related
            RETURN count(p) + count(related) AS deleted_count
        """
        
        result = session.run(query, patient_id=patient_id)
        record = result.single()
        
        deleted_count = record['deleted_count']
        return f"Deleted patient {patient_id} and {deleted_count} related nodes from Neo4j"


def neo4j_list_all_patients(tool_context: ToolContext = None) -> str:
    """List all patients in the Neo4j database.
    
    Args:
        tool_context: ADK tool context for state management
        
    Returns:
        JSON string with list of patients
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = """
            MATCH (p:Patient)
            OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
            OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m:Medication)
            RETURN p.patient_id AS patient_id,
                   p.name AS name,
                   p.created_at AS created_at,
                   count(DISTINCT c) AS condition_count,
                   count(DISTINCT m) AS medication_count
            ORDER BY p.created_at DESC
        """
        
        result = session.run(query)
        
        patients = []
        for record in result:
            patients.append({
                'patient_id': record['patient_id'],
                'name': record['name'],
                'created_at': str(record['created_at']),
                'conditions': record['condition_count'],
                'medications': record['medication_count']
            })
        
        return json.dumps({
            'total': len(patients),
            'patients': patients
        }, indent=2)


# Generic Node and Relationship Creation Tools

def neo4j_create_custom_node(
    node_id: str,
    node_label: str,
    properties: dict,
    tool_context: ToolContext
) -> str:
    """Create a custom node with any label and properties in Neo4j.
    
    Use this tool to create nodes with custom labels like Practitioner, Organization,
    LifestyleFactor, SocialDeterminant, or any other node type not covered by
    the specific creation tools.
    
    Args:
        node_id: Unique identifier for the node (will be stored as 'id' property)
        node_label: The label/type for the node (e.g., 'Practitioner', 'Organization')
        properties: Dictionary of properties to set on the node
        tool_context: ADK tool context
        
    Returns:
        Success message with node details
        
    Example:
        neo4j_create_custom_node(
            node_id="PR001",
            node_label="Practitioner",
            properties={
                "name": "Dr. Sarah Johnson",
                "specialty": "General Practitioner",
                "organization": "NHS"
            }
        )
    """
    with Neo4jClient.get_session(tool_context) as session:
        # Create node with dynamic label using MERGE to avoid duplicates
        query = f"""
            MERGE (n:{node_label} {{id: $node_id}})
            SET n += $properties
            SET n.created_at = datetime()
            RETURN n.id AS id, labels(n) AS labels
        """
        
        # Ensure id is in properties
        all_properties = {'id': node_id, **properties}
        
        result = session.run(query, node_id=node_id, properties=all_properties)
        record = result.single()
        
        return f"Created {node_label} node with id '{record['id']}' and properties: {properties}"


def neo4j_create_custom_relationship(
    from_node_id: str,
    from_node_label: str,
    to_node_id: str,
    to_node_label: str,
    relationship_type: str,
    properties: Optional[dict] = None,
    tool_context: ToolContext = None
) -> str:
    """Create a custom relationship between any two nodes in Neo4j.
    
    Use this tool to create relationships with custom types between any nodes,
    such as TREATS_CONDITION, CONTRIBUTES_TO, CARED_FOR_BY, EXHIBITS_LIFESTYLE_FACTOR, etc.
    
    Args:
        from_node_id: ID of the source node
        from_node_label: Label of the source node (e.g., 'Patient', 'Medication')
        to_node_id: ID of the target node
        to_node_label: Label of the target node (e.g., 'Condition', 'Practitioner')
        relationship_type: Type of relationship (e.g., 'TREATS_CONDITION', 'CARED_FOR_BY')
        properties: Optional dictionary of properties to set on the relationship
        tool_context: ADK tool context
        
    Returns:
        Success message with relationship details
        
    Example:
        neo4j_create_custom_relationship(
            from_node_id="M001",
            from_node_label="Medication",
            to_node_id="C001",
            to_node_label="Condition",
            relationship_type="TREATS_CONDITION",
            properties={"efficacy": "high", "indication": "primary"}
        )
    """
    with Neo4jClient.get_session(tool_context) as session:
        # Find both nodes and create relationship with dynamic type
        query = f"""
            MATCH (from:{from_node_label} {{id: $from_id}})
            MATCH (to:{to_node_label} {{id: $to_id}})
            MERGE (from)-[r:{relationship_type}]->(to)
            SET r += $properties
            SET r.created_at = datetime()
            RETURN from.id AS from_id, to.id AS to_id, type(r) AS rel_type
        """
        
        props = properties or {}
        
        result = session.run(
            query,
            from_id=from_node_id,
            to_id=to_node_id,
            properties=props
        )
        
        record = result.single()
        
        if not record:
            return f"Error: Could not find nodes with IDs '{from_node_id}' ({from_node_label}) or '{to_node_id}' ({to_node_label})"
        
        prop_str = f" with properties {properties}" if properties else ""
        return f"Created {relationship_type} relationship: {record['from_id']} -> {record['to_id']}{prop_str}"


def neo4j_delete_node(
    node_id: str,
    node_label: str,
    tool_context: ToolContext
) -> str:
    """Delete a specific node and all its relationships from Neo4j.
    
    Use this tool to remove incorrectly created nodes or clean up the graph.
    WARNING: This will also delete all relationships connected to this node.
    
    Args:
        node_id: ID of the node to delete
        node_label: Label of the node (e.g., 'ResearchArticle', 'Practitioner')
        tool_context: ADK tool context
        
    Returns:
        Success message with deletion count
        
    Example:
        neo4j_delete_node(
            node_id="PR001",
            node_label="ResearchArticle"
        )
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = f"""
            MATCH (n:{node_label} {{id: $node_id}})
            DETACH DELETE n
            RETURN count(n) AS deleted_count
        """
        
        result = session.run(query, node_id=node_id)
        record = result.single()
        
        if record['deleted_count'] == 0:
            return f"No {node_label} node found with id '{node_id}'"
        
        return f"Deleted {node_label} node '{node_id}' and all its relationships"


def neo4j_bulk_create_custom_nodes(
    nodes: list[dict],
    node_label: str,
    tool_context: ToolContext
) -> str:
    """Create multiple custom nodes with the same label in one operation.
    
    More efficient than creating nodes one at a time when you have many nodes
    to create with the same label.
    
    Args:
        nodes: List of node dictionaries, each containing 'id' and other properties
        node_label: The label for all nodes (e.g., 'Practitioner', 'LifestyleFactor')
        tool_context: ADK tool context
        
    Returns:
        Success message with count of nodes created
        
    Example:
        neo4j_bulk_create_custom_nodes(
            nodes=[
                {"id": "LF001", "name": "Poor Diet", "severity": "high"},
                {"id": "LF002", "name": "Sedentary Lifestyle", "severity": "high"}
            ],
            node_label="LifestyleFactor"
        )
    """
    with Neo4jClient.get_session(tool_context) as session:
        query = f"""
            UNWIND $nodes AS node_data
            MERGE (n:{node_label} {{id: node_data.id}})
            SET n += node_data
            SET n.created_at = datetime()
            RETURN count(n) AS created_count
        """
        
        result = session.run(query, nodes=nodes)
        record = result.single()
        
        return f"Created {record['created_count']} {node_label} nodes"


def neo4j_bulk_create_custom_relationships(
    relationships: list[dict],
    relationship_type: str,
    tool_context: ToolContext
) -> str:
    """Create multiple custom relationships of the same type in one operation.
    
    More efficient than creating relationships one at a time.
    
    Args:
        relationships: List of relationship dictionaries, each containing:
            - from_id: ID of source node
            - from_label: Label of source node
            - to_id: ID of target node
            - to_label: Label of target node
            - properties: Optional dict of relationship properties
        relationship_type: Type for all relationships (e.g., 'TREATS_CONDITION')
        tool_context: ADK tool context
        
    Returns:
        Success message with count of relationships created
        
    Example:
        neo4j_bulk_create_custom_relationships(
            relationships=[
                {"from_id": "M001", "from_label": "Medication", "to_id": "C001", "to_label": "Condition"},
                {"from_id": "M002", "from_label": "Medication", "to_id": "C001", "to_label": "Condition"}
            ],
            relationship_type="TREATS_CONDITION"
        )
    """
    created_count = 0
    
    with Neo4jClient.get_session(tool_context) as session:
        for rel in relationships:
            query = f"""
                MATCH (from:{rel['from_label']} {{id: $from_id}})
                MATCH (to:{rel['to_label']} {{id: $to_id}})
                MERGE (from)-[r:{relationship_type}]->(to)
                SET r += $properties
                SET r.created_at = datetime()
                RETURN count(r) AS count
            """
            
            props = rel.get('properties', {})
            result = session.run(
                query,
                from_id=rel['from_id'],
                to_id=rel['to_id'],
                properties=props
            )
            
            record = result.single()
            created_count += record['count']
    
    return f"Created {created_count} {relationship_type} relationships"
