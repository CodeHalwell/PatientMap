"""
Neo4j Client Manager for PatientMap

Handles Neo4j connection lifecycle using module-level singleton.
Credentials loaded from environment variables configured in .env file.

NOTE: Driver is NOT stored in ToolContext.state to avoid pickle errors
when ADK tries to deep copy sessions (SSLContext cannot be pickled).
"""

from __future__ import annotations
import os
from typing import Optional
from neo4j import GraphDatabase, Driver, Session
from google.adk.tools.tool_context import ToolContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Module-level driver singleton (not stored in session state)
_driver: Optional[Driver] = None
_database: str = 'neo4j'


class Neo4jClient:
    """Module-level Neo4j client manager (not stored in session state)"""
    
    @staticmethod
    def get_driver(tool_context: ToolContext) -> Driver:
        """Get or create Neo4j driver using module-level singleton.
        
        The driver is stored at module level to avoid pickling issues
        when ADK deep copies session state (SSLContext cannot be pickled).
        
        Args:
            tool_context: ADK tool context (not used for storage, kept for API compatibility)
            
        Returns:
            Neo4j Driver instance
            
        Raises:
            RuntimeError: If Neo4j credentials are not configured
        """
        global _driver, _database
        
        if _driver is None:
            # Get credentials from environment
            uri = os.getenv('NEO4J_URI')
            username = os.getenv('NEO4J_USERNAME')
            password = os.getenv('NEO4J_PASSWORD')
            _database = os.getenv('NEO4J_DATABASE', 'neo4j')
            
            if not all([uri, username, password]):
                raise RuntimeError(
                    "Neo4j credentials not configured. "
                    "Please set NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD in your .env file."
                )
            
            # Create driver at module level
            _driver = GraphDatabase.driver(uri, auth=(username, password))
            
            print(f"Neo4j driver initialized: {uri} (database: {_database})")
        
        return _driver
    
    @staticmethod
    def get_session(tool_context: ToolContext) -> Session:
        """Get a new Neo4j session from the driver.
        
        Args:
            tool_context: ADK tool context (not used for storage, kept for API compatibility)
            
        Returns:
            Neo4j Session instance (must be closed after use)
        """
        driver = Neo4jClient.get_driver(tool_context)
        return driver.session(database=_database)
    
    @staticmethod
    def close_driver(tool_context: ToolContext) -> None:
        """Close the Neo4j driver connection.
        
        Should be called when app shuts down (not per-session).
        
        Args:
            tool_context: ADK tool context (not used, kept for API compatibility)
        """
        global _driver
        if _driver is not None:
            _driver.close()
            _driver = None
            print("Neo4j driver closed")
    
    @staticmethod
    def verify_connection(tool_context: ToolContext) -> dict:
        """Verify Neo4j connection and return server info.
        
        Args:
            tool_context: ADK tool context (not used, kept for API compatibility)
            
        Returns:
            Dictionary with connection status and server info
        """
        try:
            driver = Neo4jClient.get_driver(tool_context)
            driver.verify_connectivity()
            
            # Get server info
            with Neo4jClient.get_session(tool_context) as session:
                result = session.run("CALL dbms.components() YIELD name, versions, edition")
                record = result.single()
                
                return {
                    'status': 'connected',
                    'database': _database,
                    'name': record['name'],
                    'versions': record['versions'],
                    'edition': record['edition']
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


def initialize_neo4j_constraints(tool_context: ToolContext) -> str:
    """Initialize Neo4j database constraints and indexes for PatientMap.
    
    Creates:
    - Unique constraint on Patient(patient_id)
    - Unique constraint on Condition(condition_id)
    - Unique constraint on Medication(medication_id)
    - Unique constraint on ResearchArticle(article_id)
    - Unique constraint on ClinicalTrial(trial_id)
    - Indexes on commonly queried properties
    
    Args:
        tool_context: ADK tool context for state management
        
    Returns:
        Success message with constraint count
    """
    constraints_created = []
    
    with Neo4jClient.get_session(tool_context) as session:
        # Patient constraints
        try:
            session.run("""
                CREATE CONSTRAINT patient_id_unique IF NOT EXISTS
                FOR (p:Patient) REQUIRE p.patient_id IS UNIQUE
            """)
            constraints_created.append("Patient.patient_id (unique)")
        except Exception as e:
            print(f"Patient constraint already exists or failed: {e}")
        
        # Condition constraints
        try:
            session.run("""
                CREATE CONSTRAINT condition_id_unique IF NOT EXISTS
                FOR (c:Condition) REQUIRE c.condition_id IS UNIQUE
            """)
            constraints_created.append("Condition.condition_id (unique)")
        except Exception as e:
            print(f"Condition constraint already exists or failed: {e}")
        
        # Medication constraints
        try:
            session.run("""
                CREATE CONSTRAINT medication_id_unique IF NOT EXISTS
                FOR (m:Medication) REQUIRE m.medication_id IS UNIQUE
            """)
            constraints_created.append("Medication.medication_id (unique)")
        except Exception as e:
            print(f"Medication constraint already exists or failed: {e}")
        
        # ResearchArticle constraints
        try:
            session.run("""
                CREATE CONSTRAINT article_id_unique IF NOT EXISTS
                FOR (a:ResearchArticle) REQUIRE a.article_id IS UNIQUE
            """)
            constraints_created.append("ResearchArticle.article_id (unique)")
        except Exception as e:
            print(f"ResearchArticle constraint already exists or failed: {e}")
        
        # ClinicalTrial constraints
        try:
            session.run("""
                CREATE CONSTRAINT trial_id_unique IF NOT EXISTS
                FOR (t:ClinicalTrial) REQUIRE t.trial_id IS UNIQUE
            """)
            constraints_created.append("ClinicalTrial.trial_id (unique)")
        except Exception as e:
            print(f"ClinicalTrial constraint already exists or failed: {e}")
        
        # Indexes for common queries
        try:
            session.run("""
                CREATE INDEX patient_name_index IF NOT EXISTS
                FOR (p:Patient) ON (p.name)
            """)
            constraints_created.append("Patient.name (index)")
        except Exception as e:
            print(f"Patient name index already exists or failed: {e}")
        
        try:
            session.run("""
                CREATE INDEX condition_label_index IF NOT EXISTS
                FOR (c:Condition) ON (c.label)
            """)
            constraints_created.append("Condition.label (index)")
        except Exception as e:
            print(f"Condition label index already exists or failed: {e}")
    
    return f"Neo4j schema initialized with {len(constraints_created)} constraints/indexes: {', '.join(constraints_created)}"
