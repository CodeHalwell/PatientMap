# Docling Complete Reference Guide

**Version:** Latest (as of retrieval)  
**Purpose:** Comprehensive guide for document processing, conversion, and AI integration using Docling

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Core Concepts](#core-concepts)
4. [Document Conversion](#document-conversion)
5. [PDF Processing Pipeline](#pdf-processing-pipeline)
6. [Advanced PDF Options](#advanced-pdf-options)
7. [Vision Language Models (VLM)](#vision-language-models-vlm)
8. [OCR Configuration](#ocr-configuration)
9. [Table Extraction](#table-extraction)
10. [Document Structure Access](#document-structure-access)
11. [Export Formats](#export-formats)
12. [Chunking & Serialization](#chunking--serialization)
13. [RAG Integrations](#rag-integrations)
14. [Enrichments](#enrichments)
15. [CLI Usage](#cli-usage)
16. [Plugins & Extensions](#plugins--extensions)
17. [Best Practices](#best-practices)
18. [API Reference](#api-reference)

---

## Introduction

**Docling** is a comprehensive Python library for document processing, conversion, and information extraction. It supports various document formats and integrates seamlessly with the generative AI ecosystem.

### Key Features

- **Multi-Format Support:** PDF, DOCX, XLSX, PPTX, HTML, Markdown, Images, Audio
- **Advanced PDF Processing:** OCR, table extraction, image extraction, structure recognition
- **Vision Language Models:** End-to-end document understanding with VLMs like GraniteDocling
- **AI Integration:** Native support for LangChain, LlamaIndex, Haystack
- **RAG-Ready:** Built-in chunking and serialization for RAG pipelines
- **Enrichments:** Code detection, formula extraction, picture description, classification
- **Hardware Acceleration:** Support for CUDA, MPS (Apple Silicon), CPU

### Architecture

```
Docling simplifies document processing by:
1. Parsing diverse formats (PDF, DOCX, HTML, etc.)
2. Advanced PDF understanding (OCR, table extraction, structure)
3. Integrating with gen AI ecosystem (embeddings, VLMs, RAG frameworks)
```

---

## Installation

### Basic Installation

```bash
pip install docling
```

### With VLM Support

```bash
pip install docling[vlm]
```

### With OCR Engines

```bash
# EasyOCR (default)
pip install docling

# Tesseract
pip install docling tesseract-ocr

# macOS-specific OCR
pip install docling ocrmac
```

### System Dependencies

#### **Ubuntu/Debian:**
```bash
apt-get install tesseract-ocr tesseract-ocr-eng libtesseract-dev libleptonica-dev pkg-config
export TESSDATA_PREFIX=$(dpkg -L tesseract-ocr-eng | grep tessdata$)
```

#### **RHEL/CentOS:**
```bash
dnf install tesseract tesseract-devel tesseract-langpack-eng tesseract-osd leptonica-devel
export TESSDATA_PREFIX=/usr/share/tesseract/tessdata/
```

#### **macOS:**
```bash
brew install tesseract leptonica pkg-config
export TESSDATA_PREFIX=/opt/homebrew/share/tessdata/
```

### Download Models Offline

```bash
# Via CLI
docling-tools models download-hf-repo ds4sd/SmolDocling-256M-preview

# Programmatically
from docling.utils.model_downloader import download_models
download_models()
```

---

## Core Concepts

### DocumentConverter

The main class for converting documents.

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")
```

### ConversionResult

Contains:
- `document`: The DoclingDocument object
- `status`: ConversionStatus (SUCCESS, PARTIAL_SUCCESS, FAILURE)
- `input`: Metadata about the input file
- `errors`: List of conversion errors

### DoclingDocument

Structured representation of a document with:
- Text items (paragraphs, headers)
- Tables
- Pictures/Figures
- Metadata
- Hierarchical structure

### InputFormat

Supported input formats:

```python
from docling.datamodel.base_models import InputFormat

InputFormat.PDF
InputFormat.DOCX
InputFormat.XLSX
InputFormat.PPTX
InputFormat.HTML
InputFormat.MD
InputFormat.ASCIIDOC
InputFormat.IMAGE
InputFormat.AUDIO
```

---

## Document Conversion

### Basic Conversion

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()

# From URL
result = converter.convert("https://arxiv.org/pdf/2408.09869")

# From local file
result = converter.convert("document.pdf")

# Access the document
doc = result.document
print(doc.export_to_markdown())
```

### Batch Conversion

```python
from pathlib import Path
from docling.datamodel.base_models import ConversionStatus

input_paths = [
    Path("document1.pdf"),
    Path("document2.docx"),
    "https://example.com/document3.pdf"
]

converter = DocumentConverter()

results = converter.convert_all(
    source=input_paths,
    raises_on_error=False,
    max_num_pages=100,
    max_file_size=50_000_000  # 50MB
)

for conv_result in results:
    if conv_result.status == ConversionStatus.SUCCESS:
        doc_filename = conv_result.input.file.stem
        conv_result.document.save_as_json(f"{doc_filename}.json")
        conv_result.document.save_as_markdown(f"{doc_filename}.md")
    elif conv_result.status == ConversionStatus.PARTIAL_SUCCESS:
        print(f"Partial success: {conv_result.input.file}")
        for error in conv_result.errors:
            print(f"  Error: {error.error_message}")
    else:
        print(f"Failed: {conv_result.input.file}")
```

### Binary Stream Conversion

```python
from io import BytesIO
from docling.datamodel.base_models import DocumentStream

buf = BytesIO(your_binary_stream)
source = DocumentStream(name="my_doc.pdf", stream=buf)
converter = DocumentConverter()
result = converter.convert(source)
```

### Multi-Format Configuration

```python
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
    ExcelFormatOption,
    PowerpointFormatOption,
    MarkdownFormatOption,
    HTMLFormatOption,
)
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

pdf_options = PdfPipelineOptions()
pdf_options.do_ocr = True
pdf_options.do_table_structure = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
        InputFormat.DOCX: WordFormatOption(),
        InputFormat.XLSX: ExcelFormatOption(),
        InputFormat.PPTX: PowerpointFormatOption(),
        InputFormat.MD: MarkdownFormatOption(),
        InputFormat.HTML: HTMLFormatOption(),
    }
)

files = ["doc.pdf", "spreadsheet.xlsx", "presentation.pptx", "readme.md"]
for file in files:
    result = converter.convert(file)
    print(f"Converted {file}: {result.status}")
```

---

## PDF Processing Pipeline

### StandardPdfPipeline

The default pipeline for PDF processing with layout detection, OCR, and table extraction.

```python
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True
pipeline_options.do_code_enrichment = True
pipeline_options.do_formula_enrichment = True
pipeline_options.generate_page_images = True
pipeline_options.generate_picture_images = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

result = converter.convert("document.pdf")
```

### SimplePipeline

For documents that don't require complex processing.

```python
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.document_converter import WordFormatOption

converter = DocumentConverter(
    format_options={
        InputFormat.DOCX: WordFormatOption(pipeline_cls=SimplePipeline)
    }
)
```

---

## Advanced PDF Options

### Complete Pipeline Configuration

```python
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    EasyOcrOptions,
    TableFormerMode,
)
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions

pipeline_options = PdfPipelineOptions()

# OCR Configuration
pipeline_options.do_ocr = True
pipeline_options.ocr_options = EasyOcrOptions(
    lang=["en", "de", "fr"],
    confidence_threshold=0.5
)

# Table Extraction
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
pipeline_options.table_structure_options.do_cell_matching = True

# Enrichments
pipeline_options.do_code_enrichment = True
pipeline_options.do_formula_enrichment = True

# Image Generation
pipeline_options.generate_page_images = True
pipeline_options.generate_picture_images = True
pipeline_options.images_scale = 2.0

# Hardware Acceleration
pipeline_options.accelerator_options = AcceleratorOptions(
    num_threads=4,
    device=AcceleratorDevice.AUTO  # or CPU, CUDA, MPS
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

### Offline/Air-Gapped Configuration

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

artifacts_path = "/local/path/to/models"

pipeline_options = PdfPipelineOptions(artifacts_path=artifacts_path)
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

---

## Vision Language Models (VLM)

### Using VLM Pipeline

VLM models provide end-to-end document understanding without traditional OCR.

```python
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel import vlm_model_specs
from docling.pipeline.vlm_pipeline import VlmPipeline

# GraniteDocling with Transformers
pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.GRANITEDOCLING_TRANSFORMERS,
    generate_page_images=True,
    force_backend_text=False
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
            pipeline_options=pipeline_options,
        ),
    }
)

result = converter.convert("complex_document.pdf")
print(result.document.export_to_markdown())
```

### Available VLM Models

```python
from docling.datamodel import vlm_model_specs

# Transformers (CPU/GPU)
vlm_model_specs.GRANITEDOCLING_TRANSFORMERS
vlm_model_specs.SMOLDOCLING_TRANSFORMERS

# MLX (Apple Silicon)
vlm_model_specs.GRANITEDOCLING_MLX
vlm_model_specs.SMOLDOCLING_MLX
```

### Custom Inline VLM

```python
from docling.datamodel.pipeline_options_vlm_model import (
    InlineVlmOptions,
    InferenceFramework,
    TransformersModelType,
    ResponseFormat
)
from docling.datamodel.accelerator_options import AcceleratorDevice

pipeline_options = VlmPipelineOptions(
    vlm_options=InlineVlmOptions(
        repo_id="ibm-granite/granite-vision-3.2-2b",
        prompt="Convert this page to markdown. Do not miss any text!",
        response_format=ResponseFormat.MARKDOWN,
        inference_framework=InferenceFramework.TRANSFORMERS,
        transformers_model_type=TransformersModelType.AUTOMODEL_VISION2SEQ,
        supported_devices=[
            AcceleratorDevice.CPU,
            AcceleratorDevice.CUDA,
            AcceleratorDevice.MPS,
        ],
        scale=2.0,
        temperature=0.0,
    )
)
```

### Remote VLM APIs

#### **OpenAI-Compatible (LM Studio, VLLM):**

```python
from docling.datamodel.pipeline_options_vlm_model import ApiVlmOptions, ResponseFormat

def openai_compatible_vlm_options(
    model: str,
    prompt: str,
    hostname_and_port: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    api_key: str = ""
):
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    return ApiVlmOptions(
        url=f"http://{hostname_and_port}/v1/chat/completions",
        params=dict(
            model=model,
            max_tokens=max_tokens,
        ),
        headers=headers,
        prompt=prompt,
        timeout=90,
        scale=2.0,
        temperature=temperature,
        response_format=ResponseFormat.MARKDOWN,
    )

# Use with VlmPipeline
pipeline_options = VlmPipelineOptions(
    vlm_options=openai_compatible_vlm_options(
        model="llama3-8b",
        prompt="Convert to markdown: #RAW_TEXT#",
        hostname_and_port="localhost:1234"
    )
)
```

#### **Ollama:**

```python
def ollama_vlm_options(model: str, prompt: str):
    return ApiVlmOptions(
        url="http://localhost:11434/v1/chat/completions",
        params=dict(model=model),
        prompt=prompt,
        timeout=90,
        scale=1.0,
        response_format=ResponseFormat.MARKDOWN,
    )
```

#### **IBM watsonx.ai:**

```python
import os
import requests
from dotenv import load_dotenv

def watsonx_vlm_options(model: str, prompt: str):
    load_dotenv()
    api_key = os.environ.get("WX_API_KEY")
    project_id = os.environ.get("WX_PROJECT_ID")
    
    def get_iam_token(api_key: str) -> str:
        res = requests.post(
            url="https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}",
        )
        res.raise_for_status()
        return res.json()["access_token"]
    
    return ApiVlmOptions(
        url="https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29",
        params=dict(
            model_id=model,
            project_id=project_id,
            parameters=dict(max_new_tokens=400),
        ),
        headers={"Authorization": f"Bearer {get_iam_token(api_key)}"},
        prompt=prompt,
        timeout=60,
        response_format=ResponseFormat.MARKDOWN,
    )
```

---

## OCR Configuration

### EasyOCR (Default)

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = EasyOcrOptions(
    lang=["en", "de", "fr", "es"],
    confidence_threshold=0.5
)
```

### Tesseract OCR

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = TesseractOcrOptions()
```

### macOS Native OCR

```python
# Install ocrmac first: pip install ocrmac
from docling.datamodel.pipeline_options import PdfPipelineOptions, OcrMacOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = OcrMacOptions()
```

### Multi-Language OCR

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.ocr_options.lang = ["fr", "de", "es", "en"]
```

---

## Table Extraction

### TableFormer Models

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

pipeline_options = PdfPipelineOptions(do_table_structure=True)

# Fast mode (default)
pipeline_options.table_structure_options.mode = TableFormerMode.FAST

# Accurate mode (better for complex tables)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

# Cell matching
pipeline_options.table_structure_options.do_cell_matching = True
```

### Extracting Tables

```python
import pandas as pd
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document_with_tables.pdf")

for table_idx, table in enumerate(result.document.tables):
    # Export to pandas DataFrame
    df = table.export_to_dataframe()
    
    # Print as Markdown
    print(f"## Table {table_idx + 1}")
    print(df.to_markdown())
    
    # Save as CSV
    df.to_csv(f"table_{table_idx + 1}.csv")
    
    # Export as HTML
    html_table = table.export_to_html(doc=result.document)
    with open(f"table_{table_idx + 1}.html", "w") as f:
        f.write(html_table)
    
    # Access properties
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
```

---

## Document Structure Access

### Iterate Through Items

```python
from docling_core.types.doc import DocItemLabel

result = converter.convert("document.pdf")
doc = result.document

# All text items
for item in doc.iterate_items():
    if item.label == DocItemLabel.TEXT or item.label == DocItemLabel.PARAGRAPH:
        print(f"Text: {item.text}")

# Section headers
headers = [item for item in doc.iterate_items() if item.label == DocItemLabel.SECTION_HEADER]
for header in headers:
    print(f"Section: {header.text}")

# Tables
for table in doc.tables:
    df = table.export_to_dataframe()
    print(f"Table: {df.shape}")

# Pictures/Figures
for picture in doc.pictures:
    print(f"Picture: {picture.caption if hasattr(picture, 'caption') else 'No caption'}")
```

### Document Metadata

```python
# File metadata
print(f"Page count: {result.input.page_count}")
print(f"File size: {result.input.filesize}")
print(f"Format: {result.input.format}")

# Page-level information
for page_num in range(result.input.page_count):
    page_items = [
        item for item in doc.iterate_items() 
        if hasattr(item, 'prov') and item.prov and len(item.prov) > 0
    ]
    print(f"Page {page_num + 1}: {len(page_items)} items")
```

### Element Tree

```python
# Print document structure
doc.print_element_tree()

# Iterate with hierarchy
from docling_core.types.doc import TextItem, TableItem

for item, level in doc.iterate_items():
    if isinstance(item, TextItem):
        print("  " * level + item.text)
    elif isinstance(item, TableItem):
        table_df = item.export_to_dataframe()
        print("  " * level + f"[Table: {table_df.shape}]")
```

---

## Export Formats

### Markdown

```python
markdown_output = result.document.export_to_markdown()
print(markdown_output)

# Save to file
result.document.save_as_markdown("output.md")
```

### JSON

```python
import json

json_dict = result.document.export_to_dict()
print(json.dumps(json_dict, indent=2))

# Save to file
result.document.save_as_json("output.json")
```

### HTML

```python
html_output = result.document.export_to_html()
print(html_output)

# Save to file
result.document.save_as_html("output.html")
```

### DocTags

```python
# Proprietary format preserving all structure
doctags = result.document.export_to_document_tokens()

# Save to file
result.document.save_as_document_tokens("output.doctags.txt")
```

### Image Handling

```python
from pathlib import Path
from docling_core.types.doc import ImageRefMode

output_dir = Path("./output")
output_dir.mkdir(exist_ok=True)

# Placeholder references
result.document.save_as_markdown(
    output_dir / "doc_placeholders.md",
    image_mode=ImageRefMode.PLACEHOLDER
)

# Embedded base64 images
result.document.save_as_html(
    output_dir / "doc_embedded.html",
    image_mode=ImageRefMode.EMBEDDED
)

# Referenced images (saves separately)
result.document.save_as_markdown(
    output_dir / "doc_refs.md",
    image_mode=ImageRefMode.REFERENCED
)
```

---

## Chunking & Serialization

### HybridChunker

Combines hierarchical and semantic chunking strategies.

```python
from docling_core.transforms.chunker import HybridChunker

chunker = HybridChunker()
chunks = list(chunker.chunk(doc))

for chunk in chunks:
    print(f"Chunk: {chunk.text[:100]}...")
    print(f"  Metadata: {chunk.meta}")
```

### With Tokenizer

```python
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

tokenizer = HuggingFaceTokenizer(
    tokenizer=AutoTokenizer.from_pretrained(EMBED_MODEL_ID)
)

chunker = HybridChunker(
    tokenizer=tokenizer,
    max_tokens=512
)

chunks = list(chunker.chunk(doc))
```

### Custom Serialization

#### **Markdown Table Serializer:**

```python
from docling_core.transforms.chunker.hierarchical_chunker import (
    ChunkingDocSerializer,
    ChunkingSerializerProvider,
)
from docling_core.transforms.serializer.markdown import MarkdownTableSerializer

class MDTableSerializerProvider(ChunkingSerializerProvider):
    def get_serializer(self, doc):
        return ChunkingDocSerializer(
            doc=doc,
            table_serializer=MarkdownTableSerializer(),
        )

chunker = HybridChunker(
    tokenizer=tokenizer,
    serializer_provider=MDTableSerializerProvider(),
)

chunks = list(chunker.chunk(doc))
```

#### **Custom Image Placeholder:**

```python
from docling_core.transforms.serializer.markdown import MarkdownParams

class ImgPlaceholderSerializerProvider(ChunkingSerializerProvider):
    def get_serializer(self, doc):
        return ChunkingDocSerializer(
            doc=doc,
            params=MarkdownParams(
                image_placeholder="<!-- image -->",
            ),
        )

chunker = HybridChunker(
    tokenizer=tokenizer,
    serializer_provider=ImgPlaceholderSerializerProvider(),
)
```

---

## RAG Integrations

### LangChain

#### **Setup:**

```python
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from docling.chunking import HybridChunker

EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

loader = DoclingLoader(
    file_path=["https://arxiv.org/pdf/2408.09869"],
    export_type=ExportType.DOC_CHUNKS,
    chunker=HybridChunker(tokenizer=EMBED_MODEL_ID),
)

docs = loader.load()
```

#### **Vector Store Ingestion:**

```python
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from pathlib import Path
from tempfile import mkdtemp

embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)

vectorstore = Milvus.from_documents(
    documents=docs,
    embedding=embedding,
    collection_name="docling_demo",
    connection_args={"uri": str(Path(mkdtemp()) / "docling.db")},
    index_params={"index_type": "FLAT"},
    drop_old=True,
)
```

#### **RAG Query:**

```python
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
    huggingfacehub_api_token=HF_TOKEN,
)

prompt = PromptTemplate.from_template(
    "Context: {context}\n\nQuestion: {input}\nAnswer:"
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

result = rag_chain.invoke({"input": "Which are the main AI models in Docling?"})
print(result["answer"])
```

### LlamaIndex

#### **Setup with DoclingReader:**

```python
from llama_index.readers.docling import DoclingReader
from llama_index.node_parser.docling import DoclingNodeParser
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from pathlib import Path
from tempfile import mkdtemp

reader = DoclingReader(export_type=DoclingReader.ExportType.JSON)
node_parser = DoclingNodeParser()

EMBED_MODEL = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
embed_dim = len(EMBED_MODEL.get_text_embedding("test"))

vector_store = MilvusVectorStore(
    uri=str(Path(mkdtemp()) / "docling.db"),
    dim=embed_dim,
    overwrite=True,
)

index = VectorStoreIndex.from_documents(
    documents=reader.load_data("https://arxiv.org/pdf/2408.09869"),
    transformations=[node_parser],
    storage_context=StorageContext.from_defaults(vector_store=vector_store),
    embed_model=EMBED_MODEL,
)
```

#### **Query:**

```python
GEN_MODEL = HuggingFaceInferenceAPI(
    token=HF_TOKEN,
    model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
)

query_engine = index.as_query_engine(llm=GEN_MODEL)
result = query_engine.query("Which are the main AI models in Docling?")

print(f"Answer: {result.response.strip()}")
for node in result.source_nodes:
    print(f"Source: {node.text[:100]}...")
```

### Haystack

#### **Setup:**

```python
from docling_haystack.converter import DoclingConverter, ExportType
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from milvus_haystack import MilvusDocumentStore
from docling.chunking import HybridChunker

EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

document_store = MilvusDocumentStore(
    connection_args={"uri": "./docling.db"},
    drop_old=True,
)

idx_pipe = Pipeline()
idx_pipe.add_component(
    "converter",
    DoclingConverter(
        export_type=ExportType.DOC_CHUNKS,
        chunker=HybridChunker(tokenizer=EMBED_MODEL_ID),
    ),
)
idx_pipe.add_component(
    "embedder",
    SentenceTransformersDocumentEmbedder(model=EMBED_MODEL_ID),
)
idx_pipe.add_component("writer", DocumentWriter(document_store=document_store))

idx_pipe.connect("converter", "embedder")
idx_pipe.connect("embedder", "writer")
idx_pipe.run({"converter": {"paths": ["https://arxiv.org/pdf/2408.09869"]}})
```

#### **RAG Pipeline:**

```python
from haystack.components.builders import PromptBuilder, AnswerBuilder
from haystack.components.generators import HuggingFaceAPIGenerator
from haystack.components.embedders import SentenceTransformersTextEmbedder
from milvus_haystack import MilvusEmbeddingRetriever

prompt_template = """
Given these documents, answer the question.
Documents:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}
Question: {{query}}
Answer:
"""

rag_pipe = Pipeline()
rag_pipe.add_component("embedder", SentenceTransformersTextEmbedder(model=EMBED_MODEL_ID))
rag_pipe.add_component("retriever", MilvusEmbeddingRetriever(document_store=document_store, top_k=3))
rag_pipe.add_component("prompt_builder", PromptBuilder(template=prompt_template))
rag_pipe.add_component("llm", HuggingFaceAPIGenerator(
    api_type="serverless_inference_api",
    api_params={"model": "mistralai/Mixtral-8x7B-Instruct-v0.1"},
))
rag_pipe.add_component("answer_builder", AnswerBuilder())

rag_pipe.connect("embedder.embedding", "retriever")
rag_pipe.connect("retriever", "prompt_builder.documents")
rag_pipe.connect("prompt_builder", "llm")
rag_pipe.connect("llm.replies", "answer_builder.replies")

result = rag_pipe.run({
    "embedder": {"text": "Which are the main AI models in Docling?"},
    "prompt_builder": {"query": "Which are the main AI models in Docling?"},
})

print(result["answer_builder"]["answers"][0].data)
```

### Qdrant

```python
from qdrant_client import QdrantClient
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter

COLLECTION_NAME = "docling"

converter = DocumentConverter()
client = QdrantClient(location=":memory:")  # or "http://localhost:6333"

client.set_model("sentence-transformers/all-MiniLM-L6-v2")
client.set_sparse_model("Qdrant/bm25")

# Convert and chunk
doc = converter.convert("document.pdf").document
chunker = HybridChunker()
chunks = [chunk.text for chunk in chunker.chunk(doc)]

# Index
client.add(
    collection_name=COLLECTION_NAME,
    documents=chunks,
)

# Query
results = client.query(
    collection_name=COLLECTION_NAME,
    query_text="What are the main findings?",
    limit=5
)
```

---

## Enrichments

### Picture Description

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.do_picture_description = True

# Default SmolVLM or Granite models
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

#### **Custom Hugging Face Model:**

```python
from docling.datamodel.pipeline_options import PictureDescriptionVlmOptions

pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
    repo_id="HuggingFaceTB/SmolVLM-256M-Instruct",
    prompt="Describe this picture in three to five sentences. Be precise.",
)
pipeline_options.images_scale = 2
pipeline_options.generate_picture_images = True
```

#### **Remote API (VLLM/Ollama/watsonx):**

```python
from docling.datamodel.pipeline_options import PictureDescriptionApiOptions

pipeline_options.enable_remote_services = True

pipeline_options.picture_description_options = PictureDescriptionApiOptions(
    url="http://localhost:8000/v1/chat/completions",
    params=dict(
        model="MODEL_NAME",
        max_completion_tokens=200,
    ),
    prompt="Describe the image briefly.",
    timeout=90,
)
```

### Picture Classification

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.generate_picture_images = True
pipeline_options.images_scale = 2
pipeline_options.do_picture_classification = True
```

### Code Understanding

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_code_enrichment = True
```

### Formula Understanding

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_formula_enrichment = True
```

---

## CLI Usage

### Basic Conversion

```bash
# From URL
docling https://arxiv.org/pdf/2206.01062

# From local file
docling document.pdf

# Specify output directory
docling document.pdf --output ./results
```

### Export Formats

```bash
# Markdown (default)
docling document.pdf --to markdown

# Multiple formats
docling document.pdf --to json --to markdown --to html
```

### Batch Processing

```bash
# Multiple files
docling file1.pdf file2.docx file3.pptx --output ./converted

# From directory
docling ./input/dir --from pdf --from docx
```

### Advanced Options

```bash
# With OCR
docling scanned.pdf --ocr --ocr-engine easyocr

# Table extraction mode
docling document.pdf --table-structure-mode accurate

# Hardware acceleration
docling document.pdf --device cuda  # or cpu, mps, auto

# Page limits
docling large_document.pdf --max-num-pages 50

# Picture and code extraction
docling document.pdf --pictures --code

# Disable OCR
docling document.pdf --no-ocr
```

### VLM Pipeline

```bash
# Default VLM
docling --pipeline vlm document.pdf

# Specific VLM model
docling --pipeline vlm --vlm-model granite_docling document.pdf
```

### Combined Options

```bash
docling document.pdf \
  --ocr \
  --ocr-engine tesseract \
  --table-structure-mode accurate \
  --device auto \
  --output ./results \
  --to markdown \
  --pictures
```

---

## Plugins & Extensions

### Plugin System

Docling supports external plugins for OCR and other functionality.

#### **Enable External Plugins:**

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.allow_external_plugins = True
pipeline_options.ocr_options = YourCustomOcrOptions()
```

#### **CLI:**

```bash
# List plugins
docling --show-external-plugins

# Use plugin
docling --allow-external-plugins --ocr-engine=custom_engine document.pdf
```

### Custom OCR Plugin

```python
# In your plugin package
def ocr_engines():
    return {
        "ocr_engines": [
            YourOcrModel,
        ]
    }
```

---

## Best Practices

### Performance Optimization

1. **Use Hardware Acceleration:**
   ```python
   pipeline_options.accelerator_options = AcceleratorOptions(
       device=AcceleratorDevice.CUDA  # or MPS for Apple Silicon
   )
   ```

2. **Limit Processing for Large Documents:**
   ```python
   converter.convert(
       "large_doc.pdf",
       max_num_pages=100,
       max_file_size=50_000_000
   )
   ```

3. **Batch Processing:**
   ```python
   results = converter.convert_all(
       source=file_list,
       raises_on_error=False
   )
   ```

### Table Extraction Tips

- Use `ACCURATE` mode for complex tables with merged cells
- Disable `do_cell_matching` if tables have merged columns
- Adjust `table_area_threshold` for better detection

### OCR Best Practices

- Use multiple languages for multilingual documents
- Adjust `confidence_threshold` based on scan quality
- Consider Tesseract for better accuracy on some documents

### Memory Management

```python
# For large document batches
import gc

for file in large_file_list:
    result = converter.convert(file)
    process_result(result)
    del result
    gc.collect()
```

### Error Handling

```python
from docling.datamodel.base_models import ConversionStatus

result = converter.convert("document.pdf")

if result.status == ConversionStatus.SUCCESS:
    # Full success
    doc = result.document
elif result.status == ConversionStatus.PARTIAL_SUCCESS:
    # Some errors but still usable
    doc = result.document
    for error in result.errors:
        print(f"Warning: {error.error_message}")
else:
    # Complete failure
    print("Conversion failed")
    for error in result.errors:
        print(f"Error: {error.error_message}")
```

---

## API Reference

### DocumentConverter

**Methods:**
- `convert(source, **kwargs)` - Convert single document
- `convert_all(source, **kwargs)` - Convert multiple documents

**Parameters:**
- `format_options`: Dict[InputFormat, FormatOption]
- `allowed_formats`: List[InputFormat]

### PdfPipelineOptions

**Key Attributes:**
- `do_ocr`: bool
- `do_table_structure`: bool
- `do_code_enrichment`: bool
- `do_formula_enrichment`: bool
- `do_picture_description`: bool
- `do_picture_classification`: bool
- `generate_page_images`: bool
- `generate_picture_images`: bool
- `images_scale`: float
- `ocr_options`: Union[EasyOcrOptions, TesseractOcrOptions, OcrMacOptions]
- `table_structure_options`: TableStructureOptions
- `accelerator_options`: AcceleratorOptions
- `artifacts_path`: Optional[str]

### DoclingDocument

**Methods:**
- `export_to_markdown()` - Export as Markdown string
- `export_to_dict()` - Export as JSON-serializable dict
- `export_to_html()` - Export as HTML string
- `export_to_document_tokens()` - Export to DocTags format
- `save_as_markdown(path, image_mode)` - Save to Markdown file
- `save_as_json(path)` - Save to JSON file
- `save_as_html(path, image_mode)` - Save to HTML file
- `iterate_items(**kwargs)` - Iterate through document items
- `print_element_tree()` - Print document structure

**Properties:**
- `tables` - List of TableItem
- `pictures` - List of PictureItem

### TableItem

**Methods:**
- `export_to_dataframe()` - Convert to pandas DataFrame
- `export_to_html(doc)` - Export to HTML string

### HybridChunker

**Constructor:**
- `HybridChunker(tokenizer=None, max_tokens=512, serializer_provider=None)`

**Methods:**
- `chunk(dl_doc)` - Generate chunks from DoclingDocument

### DocChunk

**Attributes:**
- `text` - Chunk text content
- `meta` - Chunk metadata (headings, page_no, origin, doc_items)

---

## Additional Resources

### Documentation
- Official Docs: https://docling-project.github.io/docling/
- GitHub: https://github.com/docling-project/docling

### Example Notebooks
- RAG with LangChain
- RAG with LlamaIndex
- RAG with Haystack
- Visual Grounding
- Table Extraction
- Custom Serialization

### Related Projects
- **docling-core:** Core data types and transformations
- **docling-serve:** API service for Docling
- **docling-haystack:** Haystack integration
- **docling-langchain:** LangChain integration

---

## Conclusion

Docling provides a comprehensive solution for document processing in AI applications. Its flexible architecture supports various document formats, advanced PDF understanding, and seamless integration with popular AI frameworks. Whether you're building RAG systems, extracting structured data, or processing documents at scale, Docling offers the tools you need.

**Key Takeaways:**
- Multi-format support with advanced PDF capabilities
- Vision Language Models for end-to-end understanding
- Native RAG framework integrations
- Flexible chunking and serialization
- Production-ready with hardware acceleration

For the latest features and updates, refer to the official documentation and GitHub repository.
