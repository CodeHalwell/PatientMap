# Mem0 AI - Comprehensive Reference Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation & Setup](#installation--setup)
3. [Core Concepts](#core-concepts)
4. [Configuration](#configuration)
5. [Memory Operations](#memory-operations)
6. [SDK Reference](#sdk-reference)
7. [Vector Store Integrations](#vector-store-integrations)
8. [Graph Memory](#graph-memory)
9. [Embedder Configuration](#embedder-configuration)
10. [LLM Configuration](#llm-configuration)
11. [Advanced Features](#advanced-features)
12. [Integration Examples](#integration-examples)
13. [Best Practices](#best-practices)

---

## Introduction

**Mem0** is an intelligent memory layer designed to enhance AI assistants and agents with persistent, adaptive memory capabilities. It enables AI applications to remember user preferences, context, and interactions over time, creating personalized and evolving experiences.

### Key Features
- **Persistent Memory**: Remembers across sessions and conversations
- **Multi-Level Organization**: User, Agent, and Session (Run) scopes
- **Vector & Graph Storage**: Flexible storage backends for semantic search and relationships
- **Automatic Inference**: Extracts key facts from conversations
- **Metadata Filtering**: Powerful filtering for targeted memory retrieval
- **Multi-Modal Support**: Works with various LLMs, embedders, and vector stores

### Use Cases
- Personalized AI assistants
- Customer support agents with context
- Multi-agent systems with shared memory
- Educational tutoring systems
- Collaborative task management

---

## Installation & Setup

### Basic Installation

```bash
# Python
pip install mem0ai

# JavaScript/TypeScript
npm install mem0ai
```

### Required Dependencies

```bash
# For self-hosted (OSS) deployments
pip install openai  # If using OpenAI for LLM/embeddings
pip install qdrant-client  # If using Qdrant vector store
pip install boto3  # If using AWS services
```

### Environment Variables

```python
import os

# OpenAI (for LLM and embeddings)
os.environ["OPENAI_API_KEY"] = "sk-xxx"

# Mem0 Platform (for hosted version)
os.environ["MEM0_API_KEY"] = "your-mem0-api-key"

# Google AI (if using Gemini)
os.environ["GOOGLE_API_KEY"] = "your-google-api-key"

# AWS (if using Bedrock)
# Configure via boto3 credentials

# Azure OpenAI
os.environ["EMBEDDING_AZURE_OPENAI_API_KEY"] = "your-api-key"
os.environ["EMBEDDING_AZURE_DEPLOYMENT"] = "your-deployment-name"
os.environ["EMBEDDING_AZURE_ENDPOINT"] = "your-api-base-url"
os.environ["EMBEDDING_AZURE_API_VERSION"] = "version-to-use"
```

---

## Core Concepts

### Memory Hierarchy

Mem0 organizes memories across three distinct scopes:

1. **User-Level Memory**: Personal preferences and information
2. **Agent-Level Memory**: Agent-specific behaviors and knowledge
3. **Run-Level Memory**: Session-specific context (temporary)

```python
from mem0 import Memory

memory = Memory()

# User-level memory (personal preferences)
memory.add(
    "User prefers concise responses without technical jargon",
    user_id="customer_bob"
)

# Agent-level memory (agent behaviors and knowledge)
memory.add(
    "When handling refund requests, always check order date first",
    agent_id="support_agent_v2"
)

# Run-level memory (session-specific context)
memory.add(
    "Current issue: payment failed with error code 402",
    run_id="session_12345_20250115"
)

# Search across specific scopes
user_context = memory.search("communication style", user_id="customer_bob")
agent_context = memory.search("refund process", agent_id="support_agent_v2")
session_context = memory.search("current issue", run_id="session_12345_20250115")
```

### Memory Types

- **Inferred Memories**: Automatically extracted facts from conversations
- **Raw Messages**: Store complete message history without inference
- **Metadata-Tagged**: Memories with custom metadata for filtering

---

## Configuration

### Basic Configuration (Self-Hosted)

```python
from mem0 import Memory

# Default initialization (uses in-memory vector store)
memory = Memory()
```

### Advanced Configuration

```python
from mem0 import Memory
from mem0.configs.base import MemoryConfig

config = MemoryConfig(
    vector_store={
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "my_memories"
        }
    },
    llm={
        "provider": "openai",
        "config": {
            "model": "gpt-4.1-nano-2025-04-14",
            "api_key": "sk-...",
            "temperature": 0.1,
            "max_tokens": 1000
        }
    },
    embedder={
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small"
        }
    },
    graph_store={  # Optional
        "provider": "neo4j",
        "config": {
            "url": "neo4j+s://your-instance",
            "username": "neo4j",
            "password": "password"
        }
    },
    history_db_path="~/.mem0/history.db",
    version="v1.1"
)

memory = Memory(config)
```

### Local Setup with Ollama

```python
config = MemoryConfig(
    llm={
        "provider": "ollama",
        "config": {
            "model": "llama3.1:8b",
            "ollama_base_url": "http://localhost:11434"
        }
    },
    embedder={
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text"
        }
    },
    vector_store={
        "provider": "chroma",
        "config": {
            "collection_name": "my_memories",
            "path": "./chroma_db"
        }
    }
)

memory = Memory(config)
```

### Enterprise Setup (Azure + Pinecone)

```python
config = MemoryConfig(
    llm={
        "provider": "azure_openai",
        "config": {
            "model": "gpt-4",
            "azure_endpoint": "https://your-resource.openai.azure.com/",
            "api_key": "your-api-key",
            "api_version": "2024-02-01"
        }
    },
    vector_store={
        "provider": "pinecone",
        "config": {
            "api_key": "your-pinecone-key",
            "index_name": "mem0-index",
            "dimension": 1536
        }
    }
)

memory = Memory(config)
```

---

## Memory Operations

### Adding Memories

#### From Conversation Messages

```python
from mem0 import Memory

memory = Memory()

messages = [
    {"role": "user", "content": "I love pizza and hate broccoli"},
    {"role": "assistant", "content": "I'll remember your food preferences!"}
]

# Add with automatic inference (default)
result = memory.add(
    messages=messages,
    user_id="john_doe",
    metadata={"source": "chat", "timestamp": "2025-01-15"}
)

print(result)
# Output: {'results': [{'id': 'mem_abc123', 'memory': 'User loves pizza', 'event': 'ADD'}, ...]}
```

#### Without Inference (Raw Messages)

```python
# Store raw messages without extracting facts
result = memory.add(
    messages,
    user_id="alice",
    metadata={"category": "movie_recommendations"},
    infer=False
)
```

#### Single Text Memory

```python
# Add a single memory
memory.add("I prefer vegetarian restaurants", user_id="alice")
```

#### Multi-Scope Memories

```python
# User and Agent memory
messages = [
    {"role": "user", "content": "I'm travelling to San Francisco"},
    {"role": "assistant", "content": "That's great! I'm going to Dubai next month."}
]

client.add(messages=messages, user_id="user1", agent_id="agent1")
# User message → tagged with user_id
# Assistant message → tagged with agent_id
```

### Searching Memories

#### Basic Search

```python
# Search memories for a specific user
results = memory.search("food preferences", user_id="user123")
print(results)
```

#### Context-Filtered Search

```python
# Search within specific agent and session
results = memory.search(
    query="restaurant recommendations",
    user_id="alice",
    agent_id="chatbot",
    run_id="session-123"
)
```

#### With Metadata Filters

```python
# Search with metadata filtering
results = memory.search(
    query="preferences",
    user_id="alice",
    filters={"category": "food", "priority": "high"}
)
```

### Retrieving All Memories

```python
# Get all memories for a user
all_memories = memory.get_all(user_id="user123")

# With pagination (hosted platform)
page1 = client.get_all(
    user_id="john_smith",
    page=1,
    page_size=20
)

# Filtered by scope
agent_memories = memory.get_all(user_id="alice", agent_id="diet-assistant")
session_memories = memory.get_all(user_id="alice", run_id="consultation-001")
```

### Updating Memories

```python
# Update a specific memory (hosted platform)
client.update(
    memory_id="mem_platform_abc",
    text="User is a senior software engineer at TechCorp",
    metadata={"verified": True}
)

# Batch update
client.batch_update(memories=[
    {"memory_id": "mem_1", "text": "Updated content 1"},
    {"memory_id": "mem_2", "text": "Updated content 2"}
])
```

### Deleting Memories

```python
# Delete single memory
memory.delete("memory-id")

# Delete all memories for a user
memory.delete_all(user_id="user123")

# Batch delete (hosted platform)
client.batch_delete(memories=[
    {"memory_id": "mem_old_1"},
    {"memory_id": "mem_old_2"}
])
```

### Memory History

```python
# Get memory history
history = memory.history("memory-id")
```

### Reset Memory

```python
# Reset all memories (use with caution)
memory.reset()
```

---

## SDK Reference

### Self-Hosted (OSS) SDK

#### Python

```python
from mem0 import Memory
from mem0.configs.base import MemoryConfig

# Initialize
memory = Memory()

# Or with config
config = MemoryConfig(
    vector_store={"provider": "qdrant", "config": {"host": "localhost"}},
    llm={"provider": "openai", "config": {"model": "gpt-4.1-nano-2025-04-14"}},
    embedder={"provider": "openai", "config": {"model": "text-embedding-3-small"}}
)
memory = Memory(config)

# Core operations
memory.add([{"role": "user", "content": "I love pizza"}], user_id="user123")
results = memory.search("food preferences", user_id="user123")
memory_item = memory.get("memory-id")
all_memories = memory.get_all(user_id="user123")
memory.update("memory-id", "Updated content")
memory.delete("memory-id")
memory.delete_all(user_id="user123")
history = memory.history("memory-id")
memory.reset()
```

#### TypeScript

```typescript
import { Memory } from 'mem0ai/oss';

const memory = new Memory({
  embedder: { provider: 'openai', config: { apiKey: 'key' } },
  vectorStore: { provider: 'memory', config: { dimension: 1536 } },
  llm: { provider: 'openai', config: { apiKey: 'key' } }
});

// Core operations
const result = await memory.add('My name is John', { userId: 'john' });
const searchResult = await memory.search('food preferences', { userId: 'user123' });
const memoryItem = await memory.get('memory-id');
const allMemories = await memory.getAll({ userId: 'user123' });

// Management
await memory.update('memory-id', 'Updated content');
await memory.delete('memory-id');
await memory.deleteAll({ userId: 'user123' });
await memory.reset();
```

### Hosted Platform SDK

#### Python

```python
from mem0 import MemoryClient
import os

# Initialize with API key
client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

# Add memories
result = client.add(
    messages=[{"role": "user", "content": "I work as a software engineer"}],
    user_id="john_smith",
    metadata={"conversation_id": "conv_123"}
)

# Search
results = client.search("What is my job?", user_id="john_smith", top_k=5)

# Get all with pagination
page1 = client.get_all(user_id="john_smith", page=1, page_size=20)

# Update
client.update(
    memory_id="mem_platform_abc",
    text="Updated content",
    metadata={"verified": True}
)

# Batch operations
client.batch_update(memories=[...])
client.batch_delete(memories=[...])

# User management
users = client.users()
client.delete_users(user_ids=["user1", "user2"])

# Webhooks
webhooks = client.getWebhooks()
client.createWebhook({
    "url": "https://your-webhook.com",
    "name": "My Webhook",
    "eventTypes": ["memory.created", "memory.updated"]
})
```

#### TypeScript

```typescript
import { MemoryClient } from 'mem0ai';

const client = new MemoryClient({
  apiKey: 'your-api-key',
  host: 'https://api.mem0.ai',  // optional
  organizationId: 'org-id',     // optional
  projectId: 'project-id'       // optional
});

// Core operations
const memories = await client.add([
  { role: 'user', content: 'I love pizza' }
], { user_id: 'user123' });

const results = await client.search('food preferences', { user_id: 'user123' });
const memory = await client.get('memory-id');
const allMemories = await client.getAll({ user_id: 'user123' });

// Management
await client.update('memory-id', 'Updated content');
await client.delete('memory-id');
await client.deleteAll({ user_id: 'user123' });

// Batch operations
await client.batchUpdate([{ id: 'mem1', text: 'new text' }]);
await client.batchDelete(['mem1', 'mem2']);

// User management
const users = await client.users();
await client.deleteUsers({ user_ids: ['user1', 'user2'] });
```

---

## Vector Store Integrations

Mem0 supports multiple vector database providers for flexible deployment.

### Qdrant

```python
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "test",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 1536,
            "distance": "cosine"
        }
    }
}

memory = Memory.from_config(config)
```

### Pinecone

```python
config = {
    "vector_store": {
        "provider": "pinecone",
        "config": {
            "api_key": "your-pinecone-key",
            "collection_name": "testing",
            "embedding_model_dims": 1536,
            "namespace": "my-namespace",  # Optional
            "serverless_config": {
                "cloud": "aws",  # 'aws', 'gcp', or 'azure'
                "region": "us-east-1"
            },
            "metric": "cosine"
        }
    }
}
```

### ChromaDB

```python
config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "my_memories",
            "path": "./chroma_db"
        }
    }
}
```

### FAISS

```python
config = {
    "vector_store": {
        "provider": "faiss",
        "config": {
            "collection_name": "test",
            "path": "/tmp/faiss_memories",
            "distance_strategy": "euclidean"  # or "cosine"
        }
    }
}
```

### Elasticsearch

```python
config = {
    "vector_store": {
        "provider": "elasticsearch",
        "config": {
            "collection_name": "mem0",
            "host": "localhost",
            "port": 9200,
            "embedding_model_dims": 1536
        }
    }
}
```

### Redis

```python
config = {
    "vector_store": {
        "provider": "redis",
        "config": {
            "collection_name": "mem0",
            "embedding_model_dims": 1536,
            "redis_url": "redis://localhost:6379"
        }
    }
}
```

### PostgreSQL (pgvector)

```python
config = {
    "vector_store": {
        "provider": "pgvector",
        "config": {
            "user": "test",
            "password": "123",
            "host": "127.0.0.1",
            "port": "5432",
            "dbname": "vector_store",  # Optional
            "collection_name": "memories",
            "embedding_model_dims": 1536
        }
    }
}
```

### Supabase

```python
config = {
    "vector_store": {
        "provider": "supabase",
        "config": {
            "connection_string": "postgresql://user:password@host:port/database",
            "collection_name": "memories",
            "index_method": "hnsw",  # Optional: "auto", "hnsw", "ivfflat"
            "index_measure": "cosine_distance"  # Optional
        }
    }
}
```

```sql
-- Required Supabase SQL migrations
create extension if not exists vector;

create table if not exists memories (
  id text primary key,
  embedding vector(1536),
  metadata jsonb,
  created_at timestamp with time zone default timezone('utc', now()),
  updated_at timestamp with time zone default timezone('utc', now())
);

create or replace function match_vectors(
  query_embedding vector(1536),
  match_count int,
  filter jsonb default '{}'::jsonb
)
returns table (id text, similarity float, metadata jsonb)
language plpgsql as $$
begin
  return query
  select t.id::text, 1 - (t.embedding <=> query_embedding) as similarity, t.metadata
  from memories t
  where case when filter::text = '{}'::text then true else t.metadata @> filter end
  order by t.embedding <=> query_embedding
  limit match_count;
end;
$$;
```

### AWS Neptune Analytics

```python
config = {
    "vector_store": {
        "provider": "neptune",
        "config": {
            "endpoint": "neptune-graph://my-graph-identifier",
            "collection_name": "mem0"
        }
    }
}
```

### Azure AI Search

```python
config = {
    "vector_store": {
        "provider": "azure_ai_search",
        "config": {
            "service_name": "<your-azure-ai-search-service-name>",
            "api_key": "<your-api-key>",
            "collection_name": "mem0",
            "embedding_model_dims": 1536
        }
    }
}
```

### Milvus

```python
config = {
    "vector_store": {
        "provider": "milvus",
        "config": {
            "collection_name": "test",
            "embedding_model_dims": 1536,
            "url": "127.0.0.1",
            "token": "8e4b8ca8cf2c67",
            "db_name": "my_database"
        }
    }
}
```

### OpenSearch

```python
import boto3
from opensearchpy import RequestsHttpConnection, AWSV4SignerAuth

region = 'us-west-2'
service = 'aoss'
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region, service)

config = {
    "vector_store": {
        "provider": "opensearch",
        "config": {
            "collection_name": "mem0",
            "host": "your-opensearch-domain.us-west-2.es.amazonaws.com",
            "port": 443,
            "http_auth": auth,
            "connection_class": RequestsHttpConnection,
            "pool_maxsize": 20,
            "use_ssl": True,
            "verify_certs": True,
            "embedding_model_dims": 1024
        }
    }
}
```

### LangChain Integration

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Initialize LangChain vector store
embeddings = OpenAIEmbeddings()
vector_store = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
    collection_name="mem0"  # Required
)

# Pass to Mem0
config = {
    "vector_store": {
        "provider": "langchain",
        "config": {
            "client": vector_store
        }
    }
}

memory = Memory.from_config(config)
```

---

## Graph Memory

Mem0 supports graph-based memory storage for capturing relationships between entities.

### Graph Store Providers

#### Neo4j

```python
config = {
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "neo4j+s://your-instance",
            "username": "neo4j",
            "password": "password"
        }
    }
}
```

#### Memgraph

```python
config = {
    "graph_store": {
        "provider": "memgraph",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "memgraph",
            "password": "xxx"
        }
    }
}

memory = Memory.from_config(config_dict=config)
```

#### Kuzu

```python
config = {
    "graph_store": {
        "provider": "kuzu",
        "config": {
            "db": ":memory:"  # or path to database
        }
    }
}
```

#### AWS Neptune Analytics

```python
config = {
    "graph_store": {
        "provider": "neptune",
        "config": {
            "endpoint": "neptune-graph://my-graph-identifier"
        }
    }
}
```

### Graph Memory Operations

```python
from mem0 import Memory

config = {
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "neo4j+s://your-instance",
            "username": "neo4j",
            "password": "password"
        }
    }
}

memory = Memory.from_config(config)

# Add memories with relationships
memory.add("I like pizza", user_id="alice")
memory.add("I prefer Italian cuisine", user_id="bob", agent_id="food-assistant")
memory.add("I'm allergic to peanuts", user_id="bob", agent_id="health-assistant")
memory.add("I live in Seattle", user_id="bob")  # Shared across agents

# Multi-agent context
memory.add(
    "Current session: discussing dinner plans",
    user_id="bob",
    agent_id="food-assistant",
    run_id="dinner-session-001"
)
```

---

## Embedder Configuration

### OpenAI

```python
config = {
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small",
            "api_key": "sk-xxx"
        }
    }
}
```

### Azure OpenAI

```python
config = {
    "embedder": {
        "provider": "azure_openai",
        "config": {
            "model": "text-embedding-3-large",
            "azure_kwargs": {
                "api_version": "2024-02-01",
                "azure_deployment": "your-deployment-name",
                "azure_endpoint": "your-api-base-url",
                "api_key": "your-api-key"
            }
        }
    }
}
```

### Google Gemini

```python
config = {
    "embedder": {
        "provider": "gemini",
        "config": {
            "model": "models/text-embedding-004"
        }
    }
}
```

### Vertex AI

```python
config = {
    "embedder": {
        "provider": "vertexai",
        "config": {
            "model": "text-embedding-004",
            "memory_add_embedding_type": "RETRIEVAL_DOCUMENT",
            "memory_update_embedding_type": "RETRIEVAL_DOCUMENT",
            "memory_search_embedding_type": "RETRIEVAL_QUERY"
        }
    }
}
```

### Ollama

```python
config = {
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text:latest",
            "ollama_base_url": "http://localhost:11434"
        }
    }
}
```

### LM Studio

```python
config = {
    "embedder": {
        "provider": "lmstudio",
        "config": {
            "model": "nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.f16.gguf"
        }
    }
}
```

### Cohere

```python
config = {
    "embedder": {
        "provider": "cohere",
        "config": {
            "model": "embed-english-v3.0",
            "vector_dimension": 1024
        }
    }
}
```

---

## LLM Configuration

### OpenAI

```python
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4.1-nano-2025-04-14",
            "temperature": 0.1,
            "max_tokens": 1000,
            "api_key": "sk-xxx"
        }
    }
}
```

### Azure OpenAI

```python
config = {
    "llm": {
        "provider": "azure_openai",
        "config": {
            "model": "gpt-4",
            "azure_endpoint": "https://your-resource.openai.azure.com/",
            "api_key": "your-api-key",
            "api_version": "2024-02-01"
        }
    }
}
```

### AWS Bedrock

```python
config = {
    "llm": {
        "provider": "aws_bedrock",
        "config": {
            "model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            "temperature": 0.1,
            "max_tokens": 2000
        }
    }
}
```

### Ollama

```python
config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.1:latest",
            "temperature": 0,
            "max_tokens": 2000,
            "ollama_base_url": "http://localhost:11434"
        }
    }
}
```

---

## Advanced Features

### Metadata Filtering

```python
# Add memories with metadata
memory.add(
    "I prefer vegetarian restaurants",
    user_id="alice",
    metadata={"category": "food", "priority": "high"}
)

# Search with metadata filters
results = memory.search(
    query="preferences",
    user_id="alice",
    filters={"category": "food", "priority": "high"}
)

# Enable indexing for better performance
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "indexed_fields": ["category", "priority", "status", "user_id"]
        }
    }
}
```

### Custom Prompts

```python
config = MemoryConfig(
    custom_fact_extraction_prompt="Extract key facts from the conversation...",
    custom_update_memory_prompt="Update the memory based on new information..."
)
```

### Rerankers

#### Cohere Reranker

```python
config = {
    "reranker": {
        "provider": "cohere",
        "config": {
            "model": "rerank-english-v3.0",
            "api_key": "your-cohere-api-key",
            "top_k": 5,
            "return_documents": False
        }
    }
}
```

#### Zero Entropy Reranker

```python
config = {
    "rerank": {
        "provider": "zero_entropy",
        "config": {
            "model": "zerank-1",  # or "zerank-1-small"
            "api_key": "your-zero-entropy-api-key",
            "top_k": 5
        }
    }
}
```

### OpenAI Compatibility

```python
# Mem0 OSS provides OpenAI-compatible API
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333
        }
    }
}

client = Mem0(config=config)

chat_completion = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "What's the capital of France?"}
    ],
    model="gpt-4.1-nano-2025-04-14"
)
```

---

## Integration Examples

### OpenAI Agents SDK

```python
import os
from agents import Agent, Runner, function_tool
from mem0 import MemoryClient

os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
os.environ["MEM0_API_KEY"] = "your-mem0-api-key"

mem0 = MemoryClient()

@function_tool
def search_memory(query: str, user_id: str) -> str:
    """Search through past conversations and memories"""
    memories = mem0.search(query, user_id=user_id, limit=3)
    if memories and memories.get('results'):
        return "\n".join([f"- {mem['memory']}" for mem in memories['results']])
    return "No relevant memories found."

@function_tool
def save_memory(content: str, user_id: str) -> str:
    """Save important information to memory"""
    mem0.add([{"role": "user", "content": content}], user_id=user_id)
    return "Information saved to memory."

agent = Agent(
    name="Personal Assistant",
    instructions="""You are a helpful personal assistant with memory capabilities.
    Use the search_memory tool to recall past conversations and user preferences.
    Use the save_memory tool to store important information about the user.""",
    tools=[search_memory, save_memory],
    model="gpt-4.1-nano-2025-04-14"
)

def chat_with_agent(user_input: str, user_id: str) -> str:
    result = Runner.run_sync(agent, user_input)
    return result.final_output

# Example usage
response = chat_with_agent(
    "I love Italian food and I'm planning a trip to Rome",
    user_id="alice"
)
print(response)
```

### LlamaIndex

```python
import os
from llama_index.memory.mem0 import Mem0Memory
from llama_index.core.agent import ReActAgent

os.environ["MEM0_API_KEY"] = "<your-mem0-api-key>"

# Initialize Mem0 memory
context = {"user_id": "david"}
memory = Mem0Memory.from_client(
    context=context,
    api_key=os.environ["MEM0_API_KEY"],
    search_msg_limit=4
)

# Create agent with memory
agent = ReActAgent.from_tools(
    tools=[...],
    memory=memory,
    verbose=True
)

# First interaction
response = agent.chat("Hi, My name is David")
print(response)
```

### CrewAI

```python
from crewai import Crew, Process

def setup_crew(agents: list, tasks: list):
    """Set up a crew with Mem0 memory integration"""
    return Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        memory=True,
        memory_config={
            "provider": "mem0",
            "config": {"user_id": "crew_user_1"}
        }
    )
```

### Mastra

```typescript
import { Mem0Integration } from "@mastra/mem0";

export const mem0 = new Mem0Integration({
  config: {
    apiKey: process.env.MEM0_API_KEY!,
    userId: "alice"
  }
});
```

### ElevenLabs Voice Agent

```python
from agents import Agent, function_tool
from mem0 import AsyncMemoryClient

os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
os.environ["MEM0_API_KEY"] = "your-mem0-api-key"

USER_ID = "voice_user"
mem0_client = AsyncMemoryClient()

@function_tool
async def save_memories(memory: str) -> str:
    """Store a user memory in memory."""
    memory_content = f"User memory - {memory}"
    await mem0_client.add(memory_content, user_id=USER_ID)
    return f"I've saved your memory: {memory}"

agent = Agent(
    name="Voice Assistant",
    instructions="""You are a voice assistant with memory capabilities.
    Use save_memories to store important information.""",
    tools=[save_memories],
    model="gpt-4.1-nano-2025-04-14"
)
```

### AutoGen

```python
from mem0 import Memory

# Initialize Mem0
MEM0_MEMORY_CLIENT = Memory()

USER_ID = "chicory.ai.user"
AGENT_ID = "chicory.ai"

MEMORY_DATA = """
* Preference for readability: The user prefers code to be explicitly written with clear variable names.
* Preference for comments: The user prefers comments explaining each step.
* Naming convention: The user prefers camelCase for variable names.
* Docstrings: The user prefers functions to have a descriptive docstring.
"""

# Add preference data to memory
MEM0_MEMORY_CLIENT.add(MEMORY_DATA, user_id=USER_ID)
MEM0_MEMORY_CLIENT.add(MEMORY_DATA, agent_id=AGENT_ID)
```

### Multi-Agent System

```python
class MultiAgentSystem:
    def __init__(self):
        self.shared_memory = Memory()
        self.agents = {
            "researcher": ResearchAgent(),
            "writer": WriterAgent(),
            "reviewer": ReviewAgent()
        }
    
    def collaborative_task(self, task: str, session_id: str):
        # Research phase
        research_results = self.agents["researcher"].research(task)
        self.shared_memory.add(
            f"Research findings: {research_results}",
            agent_id="researcher",
            run_id=session_id,
            metadata={"phase": "research"}
        )
        
        # Writing phase
        research_context = self.shared_memory.search(
            "research findings",
            run_id=session_id
        )
        draft = self.agents["writer"].write(task, research_context)
        self.shared_memory.add(
            f"Draft content: {draft}",
            agent_id="writer",
            run_id=session_id,
            metadata={"phase": "writing"}
        )
        
        # Review phase
        all_context = self.shared_memory.get_all(run_id=session_id)
        final_output = self.agents["reviewer"].review(draft, all_context)
        
        return final_output
```

---

## Best Practices

### 1. Choose the Right Memory Scope

```python
# User-level: Personal preferences (persistent across all sessions)
memory.add("User prefers dark mode", user_id="alice")

# Agent-level: Agent behaviors (shared knowledge for agent)
memory.add("Always greet users warmly", agent_id="customer_support_bot")

# Run-level: Session context (temporary, session-specific)
memory.add("Currently discussing order #12345", run_id="session_abc")
```

### 2. Use Metadata for Organization

```python
memory.add(
    "User loves thriller movies",
    user_id="bob",
    metadata={
        "category": "entertainment",
        "priority": "high",
        "source": "explicit_statement",
        "timestamp": "2025-01-15"
    }
)
```

### 3. Enable Field Indexing for Performance

```python
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "indexed_fields": ["category", "priority", "user_id", "timestamp"]
        }
    }
}
```

### 4. Leverage Multi-Modal Configuration

```python
# Local development
config_local = {
    "llm": {"provider": "ollama", "config": {"model": "llama3.1"}},
    "embedder": {"provider": "ollama", "config": {"model": "nomic-embed-text"}},
    "vector_store": {"provider": "chroma", "config": {"path": "./chroma_db"}}
}

# Production (multi-cloud)
config_prod = {
    "llm": {"provider": "azure_openai", "config": {...}},
    "embedder": {"provider": "vertexai", "config": {...}},
    "vector_store": {"provider": "pinecone", "config": {...}}
}
```

### 5. Implement Memory Hygiene

```python
# Regularly clean up old session memories
memory.delete_all(run_id="old_session_id")

# Update stale information
memory.update(
    memory_id="mem_123",
    text="Updated user preference",
    metadata={"last_updated": "2025-01-15"}
)
```

### 6. Use Inferred vs Raw Storage Strategically

```python
# Inferred (extract facts) - default
memory.add(messages, user_id="alice", infer=True)

# Raw (store complete messages) - for audit trails
memory.add(messages, user_id="alice", infer=False)
```

### 7. Search with Appropriate Filters

```python
# Broad search
results = memory.search("preferences", user_id="alice")

# Contextual search
results = memory.search(
    "preferences",
    user_id="alice",
    agent_id="food_bot",
    run_id="session_123",
    filters={"category": "food"}
)
```

### 8. Handle Memory Limits

```python
# Paginate when retrieving all memories
page_size = 50
page = 1
while True:
    memories = client.get_all(
        user_id="alice",
        page=page,
        page_size=page_size
    )
    if not memories:
        break
    # Process memories
    page += 1
```

### 9. Monitor Memory Usage

```python
# Track memory operations
result = memory.add(messages, user_id="alice")
for item in result['results']:
    print(f"Event: {item['event']}, Memory: {item['memory']}")
```

### 10. Secure Your API Keys

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Never hardcode API keys
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    }
}
```

---

## Additional Resources

- **Official Documentation**: https://docs.mem0.ai
- **GitHub Repository**: https://github.com/mem0ai/mem0
- **Discord Community**: Join for support and discussions
- **Cookbook Examples**: https://github.com/mem0ai/mem0/tree/main/cookbooks

---

## Version Information

This guide covers **Mem0 v1.1** (latest as of January 2025)

For version-specific features:
- **v1.1**: Graph memory, enhanced filtering, multi-provider support
- **v1.0**: Core memory operations, vector store integrations
- **v0.x**: Legacy API (deprecated)

---

## Quick Reference

### Common Patterns

```python
# 1. Initialize with defaults
memory = Memory()

# 2. Add user preference
memory.add("I prefer vegetarian food", user_id="alice")

# 3. Search memories
results = memory.search("food preferences", user_id="alice")

# 4. Get all user memories
all_memories = memory.get_all(user_id="alice")

# 5. Update memory
memory.update("memory-id", "Updated preference")

# 6. Delete memory
memory.delete("memory-id")

# 7. Add with metadata
memory.add(
    "Important info",
    user_id="alice",
    metadata={"category": "work", "priority": "high"}
)

# 8. Context-aware search
results = memory.search(
    "query",
    user_id="alice",
    agent_id="bot",
    run_id="session-123"
)
```

### Configuration Template

```python
from mem0 import Memory
from mem0.configs.base import MemoryConfig

config = MemoryConfig(
    vector_store={
        "provider": "qdrant",  # or "pinecone", "chroma", etc.
        "config": {
            "host": "localhost",
            "port": 6333
        }
    },
    llm={
        "provider": "openai",
        "config": {
            "model": "gpt-4.1-nano-2025-04-14",
            "api_key": "your-key"
        }
    },
    embedder={
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small"
        }
    }
)

memory = Memory(config)
```

---

**End of Mem0 Reference Guide**
