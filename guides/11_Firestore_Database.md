# Google Cloud Firestore Python Client - Complete Reference Guide

**Last Updated**: November 8, 2025  
**Version**: google-cloud-firestore v2.x

---

## Table of Contents

1. [Overview](#overview)
2. [Client Initialization](#client-initialization)
3. [Document Operations - Create](#document-operations---create)
4. [Document Operations - Read](#document-operations---read)
5. [Document Operations - Update and Delete](#document-operations---update-and-delete)
6. [Query Operations - Basic Queries](#query-operations---basic-queries)
7. [Query Operations - Advanced Filters](#query-operations---advanced-filters)
8. [Query Operations - Pagination](#query-operations---pagination)
9. [Collection Group Queries](#collection-group-queries)
10. [Transactions](#transactions)
11. [Batch Writes](#batch-writes)
12. [Bulk Writer](#bulk-writer)
13. [Aggregation Queries](#aggregation-queries)
14. [Real-time Listeners (Watch)](#real-time-listeners-watch)
15. [Vector Similarity Search](#vector-similarity-search)
16. [Field Path and Nested Data](#field-path-and-nested-data)
17. [Async Operations](#async-operations)
18. [Sub-collections and Document Hierarchy](#sub-collections-and-document-hierarchy)
19. [Error Handling and Retry Logic](#error-handling-and-retry-logic)
20. [Integration Patterns](#integration-patterns)

---

## Overview

Google Cloud Firestore is a fully-managed NoSQL document database for mobile, web, and server development from Firebase and Google Cloud Platform. It provides a scalable, distributed database that ensures once data is committed, it's durable even in the face of unexpected disasters. The Firestore Python client library enables developers to interact with Firestore databases using idiomatic Python code, supporting both synchronous and asynchronous operations.

**Key Features:**
- Document-oriented NoSQL database
- Real-time data synchronization with listeners
- Atomic transactions with automatic retry logic
- Flexible querying with multiple filter combinations
- Batch operations for efficient bulk writes
- Vector similarity search for ML/AI applications
- Server-side field transformations (timestamps, increments, array operations)
- Sub-collections for hierarchical data modeling
- Collection group queries for cross-hierarchy searches
- Aggregation queries for server-side analytics
- Full async/await support for non-blocking operations
- Built-in retry logic and comprehensive error handling

**Common Use Cases:**
- Mobile and web application backends
- Real-time collaborative applications
- Serverless functions with persistent storage
- User authentication and profiles
- Content management systems
- Analytics and metrics collection
- Machine learning feature stores with vector search

---

## Client Initialization

Initialize the Firestore client to connect to your database and manage all operations.

```python
from google.cloud import firestore

# Initialize client with default credentials and database
client = firestore.Client()

# Initialize with specific project and database
client = firestore.Client(
    project='my-project-id',
    database='my-database'
)

# Initialize with custom credentials
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    'path/to/service-account-key.json'
)
client = firestore.Client(
    project='my-project-id',
    credentials=credentials
)

# Access collections and documents
users_collection = client.collection('users')
user_doc = client.document('users', 'user123')

# List all top-level collections
collections = list(client.collections())
for collection in collections:
    print(f"Collection ID: {collection.id}")
```

---

## Document Operations - Create

Create new documents in Firestore collections with automatic ID generation or custom IDs.

```python
from google.cloud import firestore

client = firestore.Client()

# Create document with auto-generated ID
collection = client.collection('users')
timestamp, doc_ref = collection.add({
    'name': 'Alice Johnson',
    'email': 'alice@example.com',
    'age': 28,
    'created': firestore.SERVER_TIMESTAMP
})
print(f"Created document ID: {doc_ref.id}")
print(f"Created at: {timestamp}")

# Create document with specific ID
doc_ref = client.document('users', 'user123')
try:
    write_result = doc_ref.create({
        'name': 'Bob Smith',
        'email': 'bob@example.com',
        'age': 35,
        'metadata': {
            'registered': True,
            'subscription': 'premium'
        }
    })
    print(f"Document created at: {write_result.update_time}")
except Exception as e:
    if 'already exists' in str(e).lower():
        print("Document already exists!")
    else:
        raise
```

---

## Document Operations - Read

Retrieve documents from Firestore with various read options and error handling.

```python
from google.cloud import firestore
from google.cloud.exceptions import NotFound

client = firestore.Client()
doc_ref = client.document('users', 'user123')

# Get a document
snapshot = doc_ref.get()

if snapshot.exists:
    print(f"Document ID: {snapshot.id}")
    print(f"Document data: {snapshot.to_dict()}")
    print(f"Created: {snapshot.create_time}")
    print(f"Updated: {snapshot.update_time}")

    # Access specific fields
    data = snapshot.to_dict()
    print(f"Name: {data.get('name')}")
    print(f"Email: {data.get('email')}")
else:
    print("Document does not exist")

# Batch get multiple documents
doc_refs = [
    client.document('users', 'user123'),
    client.document('users', 'user456'),
    client.document('users', 'user789')
]
docs = client.get_all(doc_refs)
for doc in docs:
    if doc.exists:
        print(f"{doc.id}: {doc.to_dict()}")
```

---

## Document Operations - Update and Delete

Update existing documents or delete them entirely with field-level control.

```python
from google.cloud import firestore

client = firestore.Client()
doc_ref = client.document('users', 'user123')

# Update specific fields
write_result = doc_ref.update({
    'age': 29,
    'email': 'newemail@example.com',
    'updated': firestore.SERVER_TIMESTAMP
})
print(f"Updated at: {write_result.update_time}")

# Set with merge (upsert)
doc_ref.set({
    'name': 'Alice Updated',
    'lastLogin': firestore.SERVER_TIMESTAMP
}, merge=True)

# Update nested fields
doc_ref.update({
    'metadata.lastLogin': firestore.SERVER_TIMESTAMP,
    'metadata.loginCount': firestore.Increment(1)
})

# Array operations
doc_ref.update({
    'tags': firestore.ArrayUnion(['python', 'firestore']),
    'removedTags': firestore.ArrayRemove(['old-tag'])
})

# Delete specific field
doc_ref.update({
    'obsoleteField': firestore.DELETE_FIELD
})

# Delete entire document
doc_ref.delete()
print(f"Document {doc_ref.id} deleted")
```

---

## Query Operations - Basic Queries

Execute queries to retrieve filtered and ordered documents from collections.

```python
from google.cloud import firestore

client = firestore.Client()
users_collection = client.collection('users')

# Simple where clause
query = users_collection.where('age', '>=', 21)
results = query.get()
for doc in results:
    print(f"{doc.id}: {doc.to_dict()}")

# Multiple filters
query = users_collection.where('age', '>=', 21).where('age', '<=', 65)
results = query.get()

# Ordering and limiting
query = users_collection.order_by('age').limit(10)
results = query.get()

# Order descending
query = users_collection.order_by('age', direction=firestore.Query.DESCENDING).limit(5)
results = query.get()

# Complex query with multiple operations
query = (users_collection
    .where('metadata.subscription', '==', 'premium')
    .where('age', '>=', 21)
    .order_by('age')
    .order_by('name')
    .limit(20))

results = query.get()
for doc in results:
    data = doc.to_dict()
    print(f"{data['name']}, Age: {data['age']}, Subscription: {data['metadata']['subscription']}")
```

---

## Query Operations - Advanced Filters

Use composite filters with AND/OR logic for complex query conditions.

```python
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter, And, Or

client = firestore.Client()
users_collection = client.collection('users')

# OR filter
query = users_collection.where(
    filter=Or([
        FieldFilter('age', '>=', 65),
        FieldFilter('metadata.subscription', '==', 'premium')
    ])
)
results = query.get()

# AND filter (explicit)
query = users_collection.where(
    filter=And([
        FieldFilter('age', '>=', 21),
        FieldFilter('age', '<=', 65),
        FieldFilter('metadata.registered', '==', True)
    ])
)
results = query.get()

# Nested AND/OR filters
query = users_collection.where(
    filter=And([
        Or([
            FieldFilter('metadata.subscription', '==', 'premium'),
            FieldFilter('metadata.subscription', '==', 'enterprise')
        ]),
        FieldFilter('age', '>=', 18)
    ])
)

for doc in query.stream():
    print(f"{doc.id}: {doc.to_dict()}")
```

---

## Query Operations - Pagination

Implement pagination using cursors for efficient data retrieval across large result sets.

```python
from google.cloud import firestore

client = firestore.Client()
users_collection = client.collection('users')

# Initial query - first page
page_size = 10
query = users_collection.order_by('age').limit(page_size)
docs = query.get()

last_doc = None
all_results = []

for doc in docs:
    all_results.append(doc.to_dict())
    last_doc = doc
    print(f"Page 1: {doc.id}")

# Get next page using start_after cursor
if last_doc:
    next_query = users_collection.order_by('age').start_after(last_doc).limit(page_size)
    next_docs = next_query.get()

    for doc in next_docs:
        all_results.append(doc.to_dict())
        print(f"Page 2: {doc.id}")

# Alternative: start_at (inclusive)
first_doc = docs[0] if docs else None
if first_doc:
    query_from_start = users_collection.order_by('age').start_at(first_doc).limit(page_size)
    results = query_from_start.get()

# Using offset (less efficient for large datasets)
query = users_collection.order_by('age').offset(20).limit(10)
results = query.get()
```

---

## Collection Group Queries

Query across all collections with the same ID, regardless of their location in the document hierarchy.

```python
from google.cloud import firestore

client = firestore.Client()

# Query all 'reviews' subcollections across the entire database
# Structure: products/{productId}/reviews/{reviewId}
#           users/{userId}/reviews/{reviewId}

collection_group = client.collection_group('reviews')

# Get all reviews with rating >= 4
high_rated_query = collection_group.where('rating', '>=', 4)
results = high_rated_query.get()

for doc in results:
    # doc.reference.path shows the full path
    print(f"Review path: {doc.reference.path}")
    print(f"Review data: {doc.to_dict()}")

# Order and limit across all review collections
recent_reviews = (collection_group
    .order_by('timestamp', direction=firestore.Query.DESCENDING)
    .limit(10))

for doc in recent_reviews.stream():
    data = doc.to_dict()
    print(f"Rating: {data['rating']}, Comment: {data['comment']}")
    print(f"From: {doc.reference.parent.parent.path}")
```

---

## Transactions

Execute atomic read-write operations with automatic retry logic for consistency.

```python
from google.cloud import firestore

client = firestore.Client()

# Transaction function
@firestore.transactional
def transfer_balance(transaction, from_account_ref, to_account_ref, amount):
    # Read phase
    from_snapshot = from_account_ref.get(transaction=transaction)
    to_snapshot = to_account_ref.get(transaction=transaction)

    if not from_snapshot.exists:
        raise ValueError(f"Account {from_account_ref.id} does not exist")

    from_balance = from_snapshot.get('balance')
    to_balance = to_snapshot.get('balance') if to_snapshot.exists else 0

    if from_balance < amount:
        raise ValueError(f"Insufficient funds: {from_balance} < {amount}")

    # Write phase
    transaction.update(from_account_ref, {
        'balance': from_balance - amount,
        'lastTransaction': firestore.SERVER_TIMESTAMP
    })

    transaction.set(to_account_ref, {
        'balance': to_balance + amount,
        'lastTransaction': firestore.SERVER_TIMESTAMP
    }, merge=True)

    return from_balance - amount, to_balance + amount

# Execute transaction
from_ref = client.document('accounts', 'account1')
to_ref = client.document('accounts', 'account2')

transaction = client.transaction()
try:
    new_from_balance, new_to_balance = transfer_balance(
        transaction, from_ref, to_ref, 100.0
    )
    print(f"Transfer successful!")
    print(f"From balance: {new_from_balance}")
    print(f"To balance: {new_to_balance}")
except Exception as e:
    print(f"Transaction failed: {e}")
```

---

## Batch Writes

Perform multiple write operations atomically in a single batch commit.

```python
from google.cloud import firestore

client = firestore.Client()

# Create a batch
batch = client.batch()

# Add multiple operations to batch
user1_ref = client.document('users', 'user001')
batch.set(user1_ref, {
    'name': 'Alice',
    'email': 'alice@example.com',
    'created': firestore.SERVER_TIMESTAMP
})

user2_ref = client.document('users', 'user002')
batch.set(user2_ref, {
    'name': 'Bob',
    'email': 'bob@example.com',
    'created': firestore.SERVER_TIMESTAMP
})

user3_ref = client.document('users', 'user003')
batch.update(user3_ref, {
    'lastLogin': firestore.SERVER_TIMESTAMP,
    'loginCount': firestore.Increment(1)
})

user4_ref = client.document('users', 'user004')
batch.delete(user4_ref)

# Commit all operations atomically
write_results = batch.commit()
print(f"Batch committed with {len(write_results)} operations")

for i, result in enumerate(write_results):
    print(f"Operation {i+1} update_time: {result.update_time}")

# Using context manager (auto-commits on exit)
with client.batch() as batch:
    for i in range(10):
        doc_ref = client.document('products', f'product{i}')
        batch.set(doc_ref, {
            'name': f'Product {i}',
            'price': 10.0 * i,
            'inStock': True
        })
```

---

## Bulk Writer

Efficiently write large volumes of data with automatic batching and rate limiting.

```python
from google.cloud import firestore

client = firestore.Client()

# Create bulk writer
bulk_writer = client.bulk_writer()

# Callback for successful writes
def on_write_success(doc_ref, result):
    print(f"Successfully wrote {doc_ref.path} at {result.update_time}")

# Callback for failed writes
def on_write_error(doc_ref, error):
    print(f"Failed to write {doc_ref.path}: {error}")

# Write large number of documents
for i in range(1000):
    doc_ref = client.document('products', f'product_{i}')
    bulk_writer.set(
        doc_ref,
        {
            'name': f'Product {i}',
            'price': 10.0 + (i * 0.5),
            'category': f'category_{i % 10}',
            'inStock': i % 2 == 0,
            'created': firestore.SERVER_TIMESTAMP
        }
    ).add_done_callback(lambda ref=doc_ref, result=None: on_write_success(ref, result))

# Update operations
for i in range(100):
    doc_ref = client.document('users', f'user_{i}')
    bulk_writer.update(doc_ref, {
        'lastUpdated': firestore.SERVER_TIMESTAMP,
        'updateCount': firestore.Increment(1)
    })

# Close and wait for all operations to complete
bulk_writer.close()
print("All bulk operations completed")
```

---

## Aggregation Queries

Perform server-side aggregations like count, sum, and average on query results.

```python
from google.cloud import firestore

client = firestore.Client()

# Count aggregation
products_collection = client.collection('products')
count_query = products_collection.where('inStock', '==', True).count()
result = count_query.get()

print(f"Total in-stock products: {result[0][0].value}")

# Multiple aggregations
from google.cloud.firestore_v1 import aggregation

query = products_collection.where('category', '==', 'electronics')
agg_query = query.aggregate([
    aggregation.CountAggregation(alias='total_count'),
    aggregation.SumAggregation('price', alias='total_price'),
    aggregation.AvgAggregation('price', alias='average_price')
])

results = agg_query.get()
for result in results:
    print(f"Count: {result[0].value}")
    print(f"Total price: {result[1].value}")
    print(f"Average price: {result[2].value}")

# Aggregation with complex filters
orders_collection = client.collection('orders')
from google.cloud.firestore_v1.base_query import FieldFilter, And

date_query = orders_collection.where(
    filter=And([
        FieldFilter('status', '==', 'completed'),
        FieldFilter('total', '>=', 100)
    ])
)

agg_results = date_query.aggregate([
    aggregation.CountAggregation(alias='order_count'),
    aggregation.SumAggregation('total', alias='revenue')
]).get()

print(f"High-value completed orders: {agg_results[0][0].value}")
print(f"Total revenue: {agg_results[0][1].value}")
```

---

## Real-time Listeners (Watch)

Set up real-time listeners to receive updates when documents or query results change.

```python
from google.cloud import firestore
import time

client = firestore.Client()

# Document listener
def on_document_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(f"Document {doc.id} data: {doc.to_dict()}")
        print(f"Read time: {read_time}")

doc_ref = client.document('users', 'user123')
doc_watch = doc_ref.on_snapshot(on_document_snapshot)

# Collection listener with change tracking
def on_collection_snapshot(col_snapshot, changes, read_time):
    print(f"Callback received at {read_time}")

    for change in changes:
        if change.type.name == 'ADDED':
            print(f"New document: {change.document.id}")
            print(f"Data: {change.document.to_dict()}")
        elif change.type.name == 'MODIFIED':
            print(f"Modified document: {change.document.id}")
            print(f"New data: {change.document.to_dict()}")
        elif change.type.name == 'REMOVED':
            print(f"Removed document: {change.document.id}")

collection_ref = client.collection('users')
query = collection_ref.where('age', '>=', 21)
collection_watch = query.on_snapshot(on_collection_snapshot)

# Keep listener running
try:
    time.sleep(60)  # Listen for 60 seconds
except KeyboardInterrupt:
    pass
finally:
    # Unsubscribe when done
    doc_watch.unsubscribe()
    collection_watch.unsubscribe()
    print("Listeners stopped")
```

---

## Vector Similarity Search

Perform vector similarity searches for machine learning and AI applications.

```python
from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

client = firestore.Client()

# Create documents with vector embeddings
doc1_ref = client.document('products', 'product1')
doc1_ref.set({
    'name': 'Laptop Computer',
    'description': 'High-performance laptop',
    'embedding': Vector([1.0, 2.0, 3.0, 4.0, 5.0])
})

doc2_ref = client.document('products', 'product2')
doc2_ref.set({
    'name': 'Desktop Computer',
    'description': 'Powerful desktop machine',
    'embedding': Vector([1.1, 2.2, 3.1, 4.0, 5.1])
})

doc3_ref = client.document('products', 'product3')
doc3_ref.set({
    'name': 'Coffee Maker',
    'description': 'Makes great coffee',
    'embedding': Vector([8.0, 9.0, 7.5, 8.2, 9.5])
})

# Vector similarity search - Euclidean distance
collection = client.collection('products')
query_vector = Vector([1.0, 2.0, 3.0, 4.0, 5.0])

vector_query = collection.find_nearest(
    vector_field='embedding',
    query_vector=query_vector,
    distance_measure=DistanceMeasure.EUCLIDEAN,
    limit=5
)

results = vector_query.get()
for doc in results:
    data = doc.to_dict()
    print(f"Product: {data['name']}")
    print(f"Description: {data['description']}")
    print(f"Embedding: {data['embedding']}")

# Vector search with Cosine distance
vector_query = collection.find_nearest(
    vector_field='embedding',
    query_vector=query_vector,
    distance_measure=DistanceMeasure.COSINE,
    limit=3
)

results = vector_query.get()
print(f"\nFound {len(results)} similar products")
```

---

## Field Path and Nested Data

Work with nested fields using field paths for complex document structures.

```python
from google.cloud import firestore
from google.cloud.firestore_v1 import FieldPath

client = firestore.Client()

# Create document with nested structure
doc_ref = client.document('users', 'user123')
doc_ref.set({
    'name': 'Alice',
    'profile': {
        'address': {
            'street': '123 Main St',
            'city': 'San Francisco',
            'state': 'CA',
            'zip': '94102'
        },
        'preferences': {
            'theme': 'dark',
            'notifications': True
        }
    },
    'metadata': {
        'created': firestore.SERVER_TIMESTAMP,
        'tags': ['premium', 'verified']
    }
})

# Update nested fields
doc_ref.update({
    'profile.address.street': '456 Oak Ave',
    'profile.preferences.theme': 'light',
    'metadata.tags': firestore.ArrayUnion(['featured'])
})

# Query by nested field
users_collection = client.collection('users')
query = users_collection.where('profile.address.city', '==', 'San Francisco')
results = query.get()

for doc in results:
    data = doc.to_dict()
    print(f"User: {data['name']}")
    print(f"City: {data['profile']['address']['city']}")

# Use FieldPath for complex field names
doc_ref.update({
    FieldPath('profile', 'preferences', 'theme'): 'auto'
})

# Select specific fields in query
query = users_collection.select(['name', 'profile.address.city']).limit(10)
results = query.get()
```

---

## Async Operations

Use async/await syntax for non-blocking operations in asynchronous applications.

```python
import asyncio
from google.cloud import firestore

async def async_operations():
    # Create async client
    client = firestore.AsyncClient()

    try:
        # Async document creation
        doc_ref = client.document('users', 'async_user123')
        write_result = await doc_ref.set({
            'name': 'Async User',
            'email': 'async@example.com',
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        print(f"Document created at: {write_result.update_time}")

        # Async read
        snapshot = await doc_ref.get()
        if snapshot.exists:
            print(f"Data: {snapshot.to_dict()}")

        # Async query
        collection = client.collection('users')
        query = collection.where('age', '>=', 21).limit(10)

        docs = []
        async for doc in query.stream():
            docs.append(doc)
            print(f"Found: {doc.id}")

        # Async batch operations
        batch = client.batch()
        for i in range(5):
            doc_ref = client.document('async_products', f'product_{i}')
            batch.set(doc_ref, {
                'name': f'Product {i}',
                'price': 10.0 * i
            })

        await batch.commit()
        print("Batch committed")

        # Async transaction
        transaction = client.transaction()

        @firestore.async_transactional
        async def async_update(transaction):
            snapshot = await doc_ref.get(transaction=transaction)
            new_data = snapshot.to_dict()
            new_data['updated'] = firestore.SERVER_TIMESTAMP
            transaction.update(doc_ref, new_data)

        await async_update(transaction)
        print("Transaction completed")

    finally:
        # Close async client
        await client.close()

# Run async operations
asyncio.run(async_operations())
```

---

## Sub-collections and Document Hierarchy

Work with nested collections to model hierarchical data structures.

```python
from google.cloud import firestore

client = firestore.Client()

# Create document with sub-collections
user_ref = client.document('users', 'user123')
user_ref.set({
    'name': 'Alice Johnson',
    'email': 'alice@example.com'
})

# Add documents to sub-collection: users/user123/orders/order001
orders_collection = user_ref.collection('orders')
order1_ref = orders_collection.document('order001')
order1_ref.set({
    'date': firestore.SERVER_TIMESTAMP,
    'total': 99.99,
    'status': 'pending',
    'items': [
        {'product': 'Widget', 'quantity': 2, 'price': 29.99},
        {'product': 'Gadget', 'quantity': 1, 'price': 39.99}
    ]
})

# Another sub-collection: users/user123/orders/order001/items/item001
items_collection = order1_ref.collection('items')
items_collection.document('item001').set({
    'name': 'Widget',
    'quantity': 2,
    'price': 29.99
})

# Query sub-collection
user_orders = user_ref.collection('orders').where('status', '==', 'pending').get()
for order in user_orders:
    print(f"Order {order.id}: {order.to_dict()}")

# List all sub-collections of a document
collections = user_ref.collections()
for collection in collections:
    print(f"Sub-collection: {collection.id}")

# Access nested sub-collection directly
item_ref = client.document('users/user123/orders/order001/items/item001')
item_snapshot = item_ref.get()
print(f"Item: {item_snapshot.to_dict()}")

# Query across all orders for all users using collection group
all_orders = client.collection_group('orders')
high_value_orders = all_orders.where('total', '>=', 100).get()
for order in high_value_orders:
    print(f"High value order: {order.reference.path}")
```

---

## Error Handling and Retry Logic

Implement proper error handling and customize retry behavior for production applications.

```python
from google.cloud import firestore
from google.api_core import retry
from google.api_core import exceptions
from google.cloud.exceptions import NotFound, Conflict
import time

client = firestore.Client()

# Custom retry configuration
custom_retry = retry.Retry(
    initial=0.5,  # Initial delay in seconds
    maximum=60.0,  # Maximum delay
    multiplier=2.0,  # Exponential backoff multiplier
    predicate=retry.if_exception_type(
        exceptions.ServiceUnavailable,
        exceptions.DeadlineExceeded,
    )
)

# Use custom retry
doc_ref = client.document('users', 'user123')

try:
    snapshot = doc_ref.get(retry=custom_retry, timeout=30.0)
    print(f"Data: {snapshot.to_dict()}")
except NotFound:
    print("Document not found")
except exceptions.DeadlineExceeded:
    print("Request timed out")
except Exception as e:
    print(f"Error: {e}")

# Transaction with error handling
@firestore.transactional
def update_with_retry(transaction, doc_ref, updates):
    snapshot = doc_ref.get(transaction=transaction)

    if not snapshot.exists:
        raise NotFound(f"Document {doc_ref.path} not found")

    transaction.update(doc_ref, updates)
    return snapshot.to_dict()

transaction = client.transaction()
max_attempts = 3

for attempt in range(max_attempts):
    try:
        result = update_with_retry(transaction, doc_ref, {
            'counter': firestore.Increment(1),
            'lastUpdate': firestore.SERVER_TIMESTAMP
        })
        print(f"Update successful: {result}")
        break
    except Conflict:
        print(f"Conflict on attempt {attempt + 1}, retrying...")
        if attempt == max_attempts - 1:
            raise
        time.sleep(1 * (attempt + 1))
    except NotFound as e:
        print(f"Document not found: {e}")
        break
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
```

---

## Integration Patterns

### Flask Application with Firestore

```python
from flask import Flask, jsonify, request
from google.cloud import firestore

app = Flask(__name__)
db = firestore.Client()

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    doc_ref = db.collection('users').document()
    doc_ref.set({
        'name': data['name'],
        'email': data['email'],
        'created': firestore.SERVER_TIMESTAMP
    })
    return jsonify({'id': doc_ref.id}), 201

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    doc = db.collection('users').document(user_id).get()
    if doc.exists:
        return jsonify(doc.to_dict())
    return jsonify({'error': 'Not found'}), 404

@app.route('/users', methods=['GET'])
def list_users():
    docs = db.collection('users').limit(10).get()
    return jsonify([doc.to_dict() for doc in docs])
```

### Real-time Collaborative Application

```python
from google.cloud import firestore
import time

class CollaborativeEditor:
    def __init__(self, document_id):
        self.db = firestore.Client()
        self.doc_ref = self.db.collection('documents').document(document_id)
        self.changes = []

    def start_listening(self):
        def on_snapshot(doc_snapshot, changes, read_time):
            for change in changes:
                if change.type.name == 'MODIFIED':
                    print(f"Document updated: {change.document.to_dict()}")
                    self.changes.append(change.document.to_dict())

        self.doc_ref.on_snapshot(on_snapshot)

    def update_content(self, new_content):
        self.doc_ref.update({
            'content': new_content,
            'updated_by': 'current_user',
            'updated_at': firestore.SERVER_TIMESTAMP
        })

    def get_changes(self):
        return self.changes
```

### ETL Pipeline with Bulk Operations

```python
from google.cloud import firestore
from datetime import datetime

class FirestoreETL:
    def __init__(self):
        self.db = firestore.Client()

    def import_data_bulk(self, csv_file_path):
        import csv
        bulk_writer = self.db.bulk_writer()

        with open(csv_file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                doc_ref = self.db.collection('imported_data').document()
                bulk_writer.set(doc_ref, {
                    **row,
                    'imported_at': firestore.SERVER_TIMESTAMP
                })

        bulk_writer.close()

    def archive_old_records(self, days_old=30):
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)

        docs = self.db.collection('records').where(
            'created', '<', cutoff_date
        ).stream()

        batch = self.db.batch()
        for i, doc in enumerate(docs):
            batch.delete(doc.reference)
            if (i + 1) % 500 == 0:
                batch.commit()
                batch = self.db.batch()

        batch.commit()

    def analytics_aggregation(self):
        from google.cloud.firestore_v1 import aggregation

        orders = self.db.collection('orders')
        agg_results = orders.aggregate([
            aggregation.CountAggregation(alias='total_orders'),
            aggregation.SumAggregation('total', alias='revenue'),
            aggregation.AvgAggregation('total', alias='avg_order_value')
        ]).get()

        return {
            'total_orders': agg_results[0][0].value,
            'revenue': agg_results[0][1].value,
            'avg_order_value': agg_results[0][2].value
        }
```

### Machine Learning Feature Store

```python
from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
import numpy as np

class FeatureStore:
    def __init__(self):
        self.db = firestore.Client()

    def store_embedding(self, feature_id, embedding, metadata=None):
        """Store feature embeddings for similarity search."""
        doc_ref = self.db.collection('embeddings').document(feature_id)
        doc_ref.set({
            'embedding': Vector(embedding.tolist()),
            'metadata': metadata or {},
            'created': firestore.SERVER_TIMESTAMP
        })

    def find_similar(self, query_embedding, limit=5):
        """Find similar embeddings using vector search."""
        collection = self.db.collection('embeddings')
        vector_query = collection.find_nearest(
            vector_field='embedding',
            query_vector=Vector(query_embedding.tolist()),
            limit=limit
        )
        return vector_query.get()

    def bulk_store_embeddings(self, embedding_data):
        """Efficiently store multiple embeddings."""
        bulk_writer = self.db.bulk_writer()
        for feature_id, embedding in embedding_data.items():
            doc_ref = self.db.collection('embeddings').document(feature_id)
            bulk_writer.set(doc_ref, {
                'embedding': Vector(embedding.tolist()),
                'created': firestore.SERVER_TIMESTAMP
            })
        bulk_writer.close()
```

---

## Best Practices

1. **Connection Management**: Reuse Firestore client instances across your application instead of creating new ones
2. **Indexing**: Create composite indexes for complex queries involving multiple filters and ordering
3. **Data Structure**: Design document hierarchies carefully; avoid deeply nested documents (optimal depth is 5-10 levels)
4. **Batch Size**: Keep batch writes under 500 documents to avoid hitting limits
5. **Real-time Listeners**: Unsubscribe from listeners when no longer needed to avoid resource leaks
6. **Error Handling**: Always implement proper error handling and custom retry logic for production applications
7. **Async Operations**: Use async APIs for better performance in high-concurrency scenarios
8. **Security**: Use Firestore Security Rules to control access at the database level
9. **Vector Embeddings**: Pre-compute vector embeddings and store them for efficient similarity search
10. **Monitoring**: Monitor query performance using Cloud Console metrics and adjust indexes accordingly

---

## Quick Reference

| Operation | Method | Example |
|-----------|--------|---------|
| Create | `add()` or `create()` | `collection.add(data)` |
| Read | `get()` or `get_all()` | `doc_ref.get()` |
| Update | `update()` or `set(merge=True)` | `doc_ref.update(changes)` |
| Delete | `delete()` | `doc_ref.delete()` |
| Query | `where()`, `order_by()`, `limit()` | `collection.where('field', '==', value)` |
| Batch | `batch()` | `batch = client.batch()` |
| Transaction | `@firestore.transactional` | `@firestore.transactional def fn(...)` |
| Listen | `on_snapshot()` | `doc_ref.on_snapshot(callback)` |
| Bulk Write | `bulk_writer()` | `bulk_writer = client.bulk_writer()` |
| Async | `AsyncClient()` | `client = firestore.AsyncClient()` |

---

## Resources

- **Official Documentation**: https://firebase.google.com/docs/firestore
- **Python Client Library**: https://googleapis.dev/python/firestore/latest/
- **GitHub Repository**: https://github.com/googleapis/python-firestore
- **Firebase Console**: https://console.firebase.google.com/
- **Google Cloud Console**: https://console.cloud.google.com/

---

## Version History

- **v2.14.0** - Current stable release
- **v2.13.0** - Vector similarity search support
- **v2.12.0** - Aggregation queries
- **v2.0.0** - Async client support
- **v1.0.0** - Initial release
