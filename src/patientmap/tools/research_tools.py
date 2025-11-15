from google.adk.tools import AgentTool, FunctionTool
from dotenv import load_dotenv
from langchain_community.tools.google_scholar import GoogleScholarQueryRun
from langchain_community.utilities.google_scholar import GoogleScholarAPIWrapper
from langchain_community.tools.pubmed.tool import PubmedQueryRun
from langchain_community.tools.semanticscholar.tool import SemanticScholarQueryRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

load_dotenv()

def google_scholar_tool() -> AgentTool:
    """Returns a Google Scholar tool for academic research."""
    scholar_api = GoogleScholarQueryRun(api_wrapper=GoogleScholarAPIWrapper())
    
    def search_google_scholar(query: str) -> str:
        """Search Google Scholar for academic papers and citations.
        
        Args:
            query: The search query for academic literature
            
        Returns:
            Formatted results from Google Scholar
        """
        return scholar_api.run(query)
    
    return FunctionTool(func=search_google_scholar)

def pubmed_tool() -> AgentTool:
    """Returns a PubMed tool for medical literature research."""
    pubmed_api = PubmedQueryRun()
    
    def search_pubmed(query: str) -> str:
        """Search PubMed for medical research articles.
        
        Args:
            query: The search query for medical literature
            
        Returns:
            Formatted results from PubMed
        """
        return pubmed_api.run(query)
    
    return FunctionTool(func=search_pubmed)

def semantic_scholar_tool() -> AgentTool:
    """Returns a Semantic Scholar tool for academic research."""
    scholar_api = SemanticScholarQueryRun()
    
    def search_semantic_scholar(query: str) -> str:
        """Search Semantic Scholar for academic papers.

        Args:
            query: The search query for academic literature
        Returns:
            Formatted results from Semantic Scholar
        """
        return scholar_api.run(query)
    
    return FunctionTool(func=search_semantic_scholar)

def wikipedia_tool() -> AgentTool:
    """Returns a Wikipedia tool for general information retrieval."""
    wiki_api = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    
    def search_wikipedia(query: str) -> str:
        """Search Wikipedia for general information.
        
        Args:
            query: The search query for general information
            
        Returns:
            Formatted results from Wikipedia
        """
        return wiki_api.run(query)
    
    return FunctionTool(func=search_wikipedia)


