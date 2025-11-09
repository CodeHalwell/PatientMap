# NetworkX Reference Guide

> **Comprehensive documentation for network analysis and graph manipulation in Python**
>
> NetworkX is a Python library for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.
>
> **Version:** 3.0+ | **Official Docs:** https://networkx.org/

---

## Table of Contents

1. [Introduction](#introduction)
2. [Graph Types](#graph-types)
3. [Creating Graphs](#creating-graphs)
4. [Adding and Removing Elements](#adding-and-removing-elements)
5. [Graph Attributes](#graph-attributes)
6. [Accessing Graph Elements](#accessing-graph-elements)
7. [Graph Generators](#graph-generators)
8. [Graph Algorithms](#graph-algorithms)
   - [Shortest Paths](#shortest-paths)
   - [Centrality Measures](#centrality-measures)
   - [Community Detection](#community-detection)
   - [Connectivity](#connectivity)
   - [Graph Coloring](#graph-coloring)
9. [Graph Layouts and Visualization](#graph-layouts-and-visualization)
10. [Reading and Writing Graphs](#reading-and-writing-graphs)
11. [Graph Conversions](#graph-conversions)
12. [Advanced Topics](#advanced-topics)
13. [Best Practices](#best-practices)

---

## Introduction

NetworkX is designed to provide:
- **Simple, intuitive data structures** for representing graphs
- **Standard graph algorithms** implemented in Python
- **Network structure analysis** tools
- **Flexible graph generation** for various network models
- **Integration** with NumPy, SciPy, Pandas, and Matplotlib

### Key Features
- Support for directed, undirected, multigraphs, and multidigraphs
- Nodes can be any hashable object
- Edges can have arbitrary attributes
- Fast graph operations
- Extensive algorithm library

### Installation
```bash
pip install networkx
pip install matplotlib  # For visualization
pip install scipy numpy  # For advanced operations
```

---

## Graph Types

NetworkX supports four fundamental graph types:

### 1. **Graph** - Undirected Simple Graph
No self-loops, at most one edge between nodes.

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1)])
print(f"Number of edges: {G.number_of_edges()}")  # 3
```

### 2. **DiGraph** - Directed Simple Graph
Edges have direction, no parallel edges.

```python
D = nx.DiGraph()
D.add_edges_from([(1, 2), (2, 3), (3, 1), (2, 4)])

print(f"In-degree of node 2: {D.in_degree(2)}")    # 1
print(f"Out-degree of node 2: {D.out_degree(2)}")  # 2
print(f"Predecessors of 3: {list(D.predecessors(3))}")  # [2]
print(f"Successors of 2: {list(D.successors(2))}")      # [3, 4]
```

### 3. **MultiGraph** - Undirected Graph with Parallel Edges
Allows multiple edges between same pair of nodes.

```python
M = nx.MultiGraph()
M.add_edge(1, 2, key="a", weight=1.0, type="road")
M.add_edge(1, 2, key="b", weight=2.0, type="rail")
M.add_edge(2, 3, weight=3.0)

print(f"Number of edges between 1 and 2: {M.number_of_edges(1, 2)}")  # 2

# Iterate with keys
for u, v, key, data in M.edges(keys=True, data=True):
    print(f"Edge {u}-{v} (key={key}): {data}")
```

### 4. **MultiDiGraph** - Directed Graph with Parallel Edges
Combines directed edges with multi-edge capability.

```python
MD = nx.MultiDiGraph()
MD.add_edges_from([(1, 2), (1, 2), (2, 3)])
print(f"Total edges: {MD.number_of_edges()}")  # 3
```

---

## Creating Graphs

### Empty Graphs
```python
G = nx.Graph()       # Undirected
D = nx.DiGraph()     # Directed
M = nx.MultiGraph()  # Undirected multigraph
MD = nx.MultiDiGraph()  # Directed multigraph
```

### From Edge Lists
```python
# Create from edge list
edges = [(1, 2), (2, 3), (3, 4)]
G = nx.Graph(edges)

# Add edges during creation
G = nx.Graph([(1, 2, {'weight': 4}), (2, 3, {'weight': 2})])
```

### From Adjacency Dictionary
```python
adjacency_dict = {0: (1, 2), 1: (0, 2), 2: (0, 1)}
H = nx.Graph(adjacency_dict)
```

### From Another Graph
```python
G = nx.Graph()
G.add_edge(1, 2)
H = nx.DiGraph(G)  # Create DiGraph from Graph
```

### Graph Attributes on Creation
```python
G = nx.Graph(day="Friday", name="Sample Network")
print(G.graph)  # {'day': 'Friday', 'name': 'Sample Network'}
```

---

## Adding and Removing Elements

### Adding Nodes

```python
G = nx.Graph()

# Single node
G.add_node(1)
G.add_node("spam")

# Multiple nodes
G.add_nodes_from([2, 3, 4, 5])
G.add_nodes_from(range(6, 10))

# Nodes from iterable strings
G.add_nodes_from("spam")  # Adds 's', 'p', 'a', 'm'

# Nodes with attributes
G.add_node(1, time='5pm', label='Start')
G.add_nodes_from([3], time='2pm')
G.add_nodes_from([(4, {"color": "red"}), (5, {"color": "green"})])

# From another graph
H = nx.path_graph(10)
G.add_nodes_from(H)
```

### Adding Edges

```python
# Single edge (nodes created automatically)
G.add_edge(1, 2)
G.add_edge(1, 2, weight=4.7)

# Edge from tuple
e = (2, 3)
G.add_edge(*e)

# Multiple edges
G.add_edges_from([(1, 2), (1, 3), (2, 4)])
G.add_edges_from(H.edges)

# Edges with attributes
G.add_edges_from([(3, 4), (4, 5)], color='red')
G.add_edges_from([(1, 2, {'color': 'blue'}), (2, 3, {'weight': 8})])

# Weighted edges
G.add_weighted_edges_from([(1, 2, 0.5), (2, 3, 1.0), (3, 4, 2.0)])
```

### Removing Nodes

```python
G.remove_node(2)
G.remove_nodes_from([3, 4, 5])
G.remove_nodes_from("spam")

# Note: Removing a node also removes all incident edges
```

### Removing Edges

```python
G.remove_edge(1, 3)
G.remove_edges_from([(1, 2), (2, 3)])
```

### Clearing Graph

```python
G.clear()           # Remove all nodes and edges
G.clear_edges()     # Remove all edges, keep nodes
```

---

## Graph Attributes

NetworkX graphs support attributes at three levels: graph, node, and edge.

### Graph-Level Attributes

```python
G = nx.Graph(day="Friday", name="My Network")
print(G.graph)  # {'day': 'Friday', 'name': 'My Network'}

# Modify graph attributes
G.graph['day'] = 'Monday'
G.graph['created'] = '2024-01-15'
```

### Node Attributes

```python
# Add attributes when adding nodes
G.add_node(1, time='5pm', label='Start', color='red')
G.add_nodes_from([(3, {"time": "2pm"})])

# Modify node attributes
G.nodes[1]['room'] = 714
G.nodes[1]['label'] = "Starting Point"

# Access node attributes
print(G.nodes[1])  # {'time': '5pm', 'room': 714, ...}

# Get all nodes with data
print(list(G.nodes(data=True)))

# Remove node attribute
del G.nodes[1]['room']
```

### Edge Attributes

```python
# Add attributes when adding edges
G.add_edge(1, 2, weight=4.7, label='connection')
G.add_edges_from([(3, 4), (4, 5)], color='red')
G.add_edges_from([(1, 2, {'color': 'blue'}), (2, 3, {'weight': 8})])

# Modify edge attributes using subscript notation
G[1][2]['weight'] = 4.7
G.edges[3, 4]['weight'] = 4.2

# Access edge attributes
print(G.edges[1, 2])  # {'weight': 4.7, 'color': 'blue'}

# Get all edges with data
print(list(G.edges(data=True)))

# Access specific attribute
for u, v, weight in G.edges(data='weight'):
    if weight is not None and weight < 0.5:
        print(f"({u}, {v}, {weight:.3})")
```

### Special Edge Attribute: **weight**
The 'weight' attribute is recognized by many algorithms (Dijkstra, etc.):

```python
G.add_edge(1, 2, weight=4.7)
G.add_weighted_edges_from([(1, 2, 0.5), (2, 3, 1.0)])

# Algorithms will use weights
path = nx.shortest_path(G, source=1, target=3, weight='weight')
```

---

## Accessing Graph Elements

### Nodes

```python
# View nodes
print(G.nodes())          # NodeView
print(list(G.nodes))      # Convert to list

# Check node membership
if 1 in G:
    print("Node 1 exists")

print(G.has_node(1))      # True/False

# Get node data
print(G.nodes[1])         # Node attribute dict
print(list(G.nodes(data=True)))  # All nodes with attributes

# Count nodes
print(G.number_of_nodes())
print(len(G))  # Same as number_of_nodes()
```

### Edges

```python
# View edges
print(G.edges())          # EdgeView
print(list(G.edges))      # Convert to list

# Check edge existence
print(G.has_edge(1, 2))   # True/False

# Get edge data
print(G.edges[1, 2])      # Edge attribute dict
print(G.get_edge_data(1, 2))  # Alternative method

# All edges with data
for u, v, data in G.edges(data=True):
    print(f"{u}-{v}: {data}")

# Edges for specific nodes
print(list(G.edges([1, 2])))  # Edges incident to nodes 1 and 2

# Count edges
print(G.number_of_edges())
print(G.size())  # Same as number_of_edges()
```

### Neighbors and Adjacency

```python
# Get neighbors
print(list(G.neighbors(1)))  # All nodes connected to node 1
print(list(G[1]))            # Alternative syntax

# Adjacency dictionary
print(G[1])                  # Dict of neighbors
print(G.adj[1])              # Same as G[1]

# Iterate adjacency
for node, neighbors in G.adjacency():
    print(f"{node}: {list(neighbors.keys())}")

# For weighted graphs
for n, nbrs in G.adj.items():
    for nbr, eattr in nbrs.items():
        wt = eattr.get('weight', 1)
        print(f"({n}, {nbr}, {wt:.3})")
```

### Degree

```python
# Degree of single node
print(G.degree(1))
print(G.degree[1])

# Degree of multiple nodes
print(G.degree([1, 2, 3]))
print(dict(G.degree([1, 2, 3])))

# All degrees
print(dict(G.degree()))

# Weighted degree
print(G.degree(1, weight='weight'))

# Sorted degrees
print(sorted(d for n, d in G.degree()))
```

### For Directed Graphs

```python
D = nx.DiGraph()
D.add_edges_from([(1, 2), (2, 3), (3, 1)])

# In-degree and out-degree
print(D.in_degree(2))      # Number of incoming edges
print(D.out_degree(2))     # Number of outgoing edges
print(D.degree(2))         # Total (in + out)

# Weighted degrees
print(D.in_degree(2, weight='weight'))
print(D.out_degree(2, weight='weight'))

# Predecessors and successors
print(list(D.predecessors(3)))  # Nodes with edges to 3
print(list(D.successors(2)))    # Nodes with edges from 2

# In-edges and out-edges
print(list(D.in_edges(3)))   # Edges coming into 3
print(list(D.out_edges(2)))  # Edges going out from 2
```

---

## Graph Generators

NetworkX provides numerous built-in graph generators for creating common graph structures.

### Classic Graphs

```python
# Complete graph (all nodes connected)
K5 = nx.complete_graph(5)
print(f"K5: {K5.number_of_nodes()} nodes, {K5.number_of_edges()} edges")  # 5 nodes, 10 edges

# Complete bipartite graph
K_3_5 = nx.complete_bipartite_graph(3, 5)

# Path graph (nodes in a line)
P10 = nx.path_graph(10)
print(list(P10.edges())[:5])  # [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]

# Cycle graph (circular)
C6 = nx.cycle_graph(6)

# Star graph (one center connected to all others)
S7 = nx.star_graph(7)
print(f"Star center degree: {S7.degree(0)}")  # 7

# Wheel graph (star plus cycle)
W10 = nx.wheel_graph(10)

# Ladder graph
L5 = nx.ladder_graph(5)

# Barbell graph (two complete graphs connected by a path)
barbell = nx.barbell_graph(10, 10)

# Lollipop graph (complete graph + path)
lollipop = nx.lollipop_graph(10, 20)
```

### Tree Structures

```python
# Balanced tree
tree = nx.balanced_tree(r=2, h=3)  # Binary tree of height 3
print(f"Tree has {tree.number_of_nodes()} nodes")  # 15 nodes

# Random tree
rtree = nx.random_tree(n=20, seed=42)
```

### Grid Graphs

```python
# 2D grid
grid = nx.grid_2d_graph(4, 5)  # 4x5 grid
print(f"Grid has {grid.number_of_nodes()} nodes")  # 20 nodes

# Nodes are tuples: (0,0), (0,1), ...
print(grid.nodes())

# Higher dimensional grids
grid_3d = nx.grid_graph(dim=[3, 4, 5])  # 3D grid
```

### Random Graphs

```python
# Erdős-Rényi (G(n, p) model)
er_graph = nx.erdos_renyi_graph(n=100, p=0.05, seed=42)
print(f"Erdos-Renyi: {er_graph.number_of_edges()} edges")

# Watts-Strogatz (small-world)
ws_graph = nx.watts_strogatz_graph(n=100, k=4, p=0.1, seed=42)
print(f"Watts-Strogatz: {ws_graph.number_of_edges()} edges")

# Barabási-Albert (preferential attachment)
ba_graph = nx.barabasi_albert_graph(n=100, m=2, seed=42)
print(f"Barabasi-Albert: {ba_graph.number_of_edges()} edges")

# Random powerlaw tree
random_tree = nx.random_powerlaw_tree(n=50, seed=42)

# Random lobster graph
red = nx.random_lobster(100, 0.9, 0.9)
```

### Special Graphs

```python
# Petersen graph
petersen = nx.petersen_graph()

# Dodecahedral graph
dodec = nx.dodecahedral_graph()

# Karate club graph (famous social network)
karate = nx.karate_club_graph()

# Random geometric graph
rgg = nx.random_geometric_graph(200, 0.125, seed=896803)
```

---

## Graph Algorithms

### Shortest Paths

#### Single Source Shortest Paths

```python
G = nx.Graph()
G.add_edge("A", "B", weight=4)
G.add_edge("B", "D", weight=2)
G.add_edge("A", "C", weight=3)
G.add_edge("C", "D", weight=4)
G.add_edge("B", "C", weight=1)
G.add_edge("D", "E", weight=5)

# Single shortest path
path = nx.shortest_path(G, source="A", target="E", weight="weight")
print(f"Shortest path A to E: {path}")  # ['A', 'B', 'C', 'D', 'E']

# Path length
length = nx.shortest_path_length(G, source="A", target="E", weight="weight")
print(f"Path length: {length}")  # 11

# All shortest paths from a source
paths_from_A = nx.shortest_path(G, source="A", weight="weight")
print(f"Path from A to D: {paths_from_A['D']}")

# All shortest path lengths from a source
lengths = nx.shortest_path_length(G, source="A", weight="weight")
for node, dist in lengths.items():
    print(f"Distance A to {node}: {dist}")
```

#### All Pairs Shortest Paths

```python
# All pairs shortest paths
sp = dict(nx.all_pairs_shortest_path(G))
print(sp[3])  # Paths from node 3 to all others

# With weights (Dijkstra)
all_pairs_paths = dict(nx.all_pairs_dijkstra(G, weight='weight'))
for source, (distances, paths) in all_pairs_paths.items():
    print(f"From {source}: {distances}")
```

#### Alternative Shortest Paths

```python
# Find all shortest paths (multiple paths with same length)
for path in nx.all_shortest_paths(G, source="A", target="D", weight="weight"):
    print(f"Alternative path: {path}")
```

#### Unweighted Shortest Path (BFS)

```python
H = nx.path_graph(10)
path = nx.shortest_path(H, source=0, target=9)
print(f"Unweighted path: {path}")  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

#### Check Path Existence

```python
if nx.has_path(G, "A", "E"):
    print("Path exists between A and E")
```

#### Bellman-Ford Algorithm (handles negative weights)

```python
# Single source Bellman-Ford
length, path = nx.single_source_bellman_ford(G, source=0)
print(length[4])  # Distance to node 4
print(path[4])    # Path to node 4

# With target
length, path = nx.single_source_bellman_ford(G, source=0, target=1)
print(length)  # Distance to target
print(path)    # Path to target
```

### Centrality Measures

#### Degree Centrality

```python
# Measures importance based on number of connections
degree_centrality = nx.degree_centrality(G)
print(degree_centrality)

# For directed graphs
in_degree_cent = nx.in_degree_centrality(D)
out_degree_cent = nx.out_degree_centrality(D)
```

#### Betweenness Centrality

```python
# Measures importance based on shortest paths passing through node
centrality = nx.betweenness_centrality(H, k=10, endpoints=True)

# With weights
centrality = nx.betweenness_centrality(G, weight='weight')

# Edge betweenness centrality
edge_centrality = nx.edge_betweenness_centrality(G, weight='weight')
print(edge_centrality)
```

#### Closeness Centrality

```python
# Reciprocal of average shortest path distance
closeness = nx.closeness_centrality(G, distance='weight', wf_improved=True)
print(closeness)

# For specific node
closeness_u = nx.closeness_centrality(G, u=node, distance='weight')
```

#### Harmonic Centrality

```python
# Sum of reciprocals of shortest path distances
harmonic = nx.harmonic_centrality(G, distance='weight')
print(harmonic)

# From specific sources
harmonic_sources = nx.harmonic_centrality(G, sources=[1, 2, 3])
```

#### Betweenness for Node Subsets

```python
# Betweenness considering only paths between specific subsets
sources = [1, 2]
targets = [4, 5]
subset_betweenness = nx.betweenness_centrality_subset(
    G, sources, targets, normalized=False, weight=None
)
print(subset_betweenness)

# Edge betweenness for subsets
edge_subset = nx.edge_betweenness_centrality_subset(
    G, sources, targets, normalized=False, weight=None
)
```

### Community Detection

#### Girvan-Newman Algorithm

```python
# Iteratively removes highest betweenness edges
G = nx.karate_club_graph()
communities = list(nx.community.girvan_newman(G))

# Get first k levels
import itertools
k = 2
comp = nx.community.girvan_newman(G)
for communities in itertools.islice(comp, k):
    print(tuple(sorted(c) for c in communities))

# With custom edge selection
from networkx import edge_betweenness_centrality as betweenness

def most_central_edge(G):
    centrality = betweenness(G, weight="weight")
    return max(centrality, key=centrality.get)

comp = nx.community.girvan_newman(G, most_valuable_edge=most_central_edge)
```

#### Louvain Method

```python
# Modularity-based community detection
communities = nx.community.louvain_communities(G, resolution=1.0, seed=42)
for i, comm in enumerate(communities):
    print(f"Community {i}: {comm}")

# Get partition (node to community mapping)
partition = nx.community.louvain_partitions(G, resolution=1.0, seed=42)
```

#### Label Propagation

```python
# Fast label propagation algorithm
communities = nx.community.label_propagation_communities(G)
for comm in communities:
    print(comm)

# Asynchronous label propagation
communities = nx.community.asyn_lpa_communities(G, weight='weight', seed=42)
```

#### Modularity

```python
# Measure quality of community structure
modularity = nx.community.modularity(G, communities)
print(f"Modularity: {modularity}")
```

#### Edge Betweenness Partition

```python
# Partition by removing high betweenness edges
partition = nx.community.edge_betweenness_partition(G, number_of_sets=2)
for community in partition:
    print(community)
```

### Connectivity

#### Connected Components

```python
# For undirected graphs
components = nx.connected_components(G)
largest_cc = max(components, key=len)
H = G.subgraph(largest_cc)

# Number of connected components
num_components = nx.number_connected_components(G)

# Check if graph is connected
is_connected = nx.is_connected(G)
```

#### Strongly Connected Components (Directed)

```python
# For directed graphs
scc = nx.strongly_connected_components(D)
for component in scc:
    print(component)

# Largest strongly connected component
largest_scc = max(nx.strongly_connected_components(D), key=len)
```

#### Node Connectivity

```python
# Minimum number of nodes to disconnect graph
node_conn = nx.node_connectivity(G)
print(f"Node connectivity: {node_conn}")

# Between specific nodes
conn = nx.local_node_connectivity(G, source, target)
```

#### Edge Connectivity

```python
# Minimum number of edges to disconnect graph
edge_conn = nx.edge_connectivity(G)
print(f"Edge connectivity: {edge_conn}")

# Between specific nodes
conn = nx.local_edge_connectivity(G, source, target, cutoff=None)
```

#### K-Components

```python
# Find k-edge-components
k_edge_comps = nx.k_edge_components(G, k=2)
for comp in k_edge_comps:
    print(f"2-edge-component: {comp}")

# Find k-edge-subgraphs
k_edge_subgraphs = nx.k_edge_subgraphs(G, k=3)
for subgraph in k_edge_subgraphs:
    print(f"3-edge-subgraph: {subgraph.nodes()}")
```

#### Minimum Cuts

```python
# Minimum edge cut
min_cut = nx.minimum_edge_cut(G, s=source, t=target)
print(f"Minimum edge cut: {min_cut}")

# Minimum node cut
min_node_cut = nx.minimum_node_cut(G, s=source, t=target)
print(f"Minimum node cut: {min_node_cut}")
```

### Graph Coloring

```python
# Greedy graph coloring
coloring = nx.greedy_color(G, strategy='largest_first')
print(coloring)  # {node: color}

# Strategies: 'largest_first', 'smallest_last', 'random_sequential', 
#             'connected_sequential', 'saturation_largest_first'

# Number of colors used
num_colors = max(coloring.values()) + 1
print(f"Chromatic number (upper bound): {num_colors}")
```

### Graph Summarization

#### SNAP Algorithm

```python
# Summarize graph by grouping nodes with same attributes
nodes = {
    "A": {"color": "Red"},
    "B": {"color": "Red"},
    "C": {"color": "Red"},
    "E": {"color": "Blue"},
    "F": {"color": "Blue"},
}
edges = [
    ("A", "E", "Strong"),
    ("B", "F", "Strong"),
    ("C", "E", "Weak"),
]

G = nx.Graph()
for node, attrs in nodes.items():
    G.add_node(node, **attrs)
for source, target, edge_type in edges:
    G.add_edge(source, target, type=edge_type)

# Create summary graph
summary = nx.snap_aggregation(
    G, 
    node_attributes=("color",), 
    edge_attributes=("type",),
    prefix="S-"
)
print(f"Original: {G.number_of_nodes()} nodes")
print(f"Summary: {summary.number_of_nodes()} supernodes")
```

### Other Algorithms

```python
# Clustering coefficient
clustering = nx.clustering(G)
print(clustering)

# Average clustering
avg_clustering = nx.average_clustering(G)

# Transitivity
transitivity = nx.transitivity(G)

# Triangles
triangles = nx.triangles(G)

# Check if graph is planar
is_planar, embedding = nx.check_planarity(G)

# Topological sort (for DAGs)
if nx.is_directed_acyclic_graph(D):
    topo_order = list(nx.topological_sort(D))
```

---

## Graph Layouts and Visualization

NetworkX integrates with Matplotlib for graph visualization.

### Basic Drawing

```python
import matplotlib.pyplot as plt
import networkx as nx

G = nx.karate_club_graph()

# Basic drawing with default layout
plt.figure(figsize=(12, 8))
nx.draw(G, with_labels=True, node_color="lightblue",
        node_size=500, font_size=10, font_weight="bold")
plt.title("Karate Club Network")
plt.axis("off")
plt.show()
```

### Layout Algorithms

```python
# Spring layout (Fruchterman-Reingold force-directed)
pos = nx.spring_layout(G, seed=42, k=0.3, iterations=50)

# Circular layout
pos_circular = nx.circular_layout(G)

# Spectral layout
pos_spectral = nx.spectral_layout(G, dim=2)

# Kamada-Kawai layout
pos_kk = nx.kamada_kawai_layout(G)

# Shell layout
shells = [[2, 3, 4, 5, 6], [8, 1, 0, 19, 18, 17, 16, 15, 14, 7], 
          [9, 10, 11, 12, 13]]
pos_shell = nx.shell_layout(G, nlist=shells)

# Random layout
pos_random = nx.random_layout(G, seed=42)

# Planar layout (for planar graphs)
if nx.is_planar(G):
    pos_planar = nx.planar_layout(G)

# For trees - hierarchical layout
if nx.is_tree(G):
    pos_tree = nx.nx_agraph.graphviz_layout(G, prog='dot')  # Requires pygraphviz

# Grid layout
pos_grid = {(x, y): (x, y) for x, y in G.nodes()}  # For grid graphs
```

### Advanced Drawing

```python
# Calculate node properties
degree_centrality = nx.degree_centrality(G)
betweenness = nx.betweenness_centrality(G)
communities = list(nx.community.greedy_modularity_communities(G))

# Create community mapping
community_map = {}
for i, comm in enumerate(communities):
    for node in comm:
        community_map[node] = i

# Prepare visualization
pos = nx.spring_layout(G, seed=42, k=0.5)

# Node colors by community
node_colors = [community_map[node] for node in G.nodes()]

# Node sizes by betweenness centrality
node_sizes = [3000 * betweenness[node] + 100 for node in G.nodes()]

# Edge widths by weight (if available)
edge_widths = [G[u][v].get('weight', 1.0) for u, v in G.edges()]

# Create figure
fig, ax = plt.subplots(figsize=(14, 10))

# Draw network
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                       cmap=plt.cm.Set3, alpha=0.8, ax=ax)
nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.3, ax=ax)
nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold", ax=ax)

ax.set_title("Network Visualization", fontsize=16, fontweight="bold")
ax.axis("off")
plt.tight_layout()
plt.show()
```

### Drawing Options

```python
options = {
    'node_color': 'black',
    'node_size': 100,
    'width': 3,
    'edge_color': 'gray',
    'with_labels': True,
    'font_size': 12,
    'font_color': 'white',
    'font_weight': 'bold',
    'alpha': 0.7,
}

nx.draw(G, pos, **options)
```

### Drawing Subgraphs and Multiple Graphs

```python
fig, axes = plt.subplots(2, 2, figsize=(15, 15))

# Different layouts
nx.draw_random(G, ax=axes[0, 0], **options)
axes[0, 0].set_title("Random Layout")

nx.draw_circular(G, ax=axes[0, 1], **options)
axes[0, 1].set_title("Circular Layout")

nx.draw_spectral(G, ax=axes[1, 0], **options)
axes[1, 0].set_title("Spectral Layout")

nx.draw_shell(G, ax=axes[1, 1], **options)
axes[1, 1].set_title("Shell Layout")

plt.tight_layout()
plt.show()
```

### Save Graph Drawing

```python
nx.draw(G, pos)
plt.savefig("graph.png", dpi=300, bbox_inches='tight')
plt.savefig("graph.pdf")  # Vector format
```

---

## Reading and Writing Graphs

NetworkX supports various file formats for saving and loading graphs.

### Edge List Format

```python
import tempfile
import os

# Write edge list (simple format)
with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".edgelist") as f:
    edgelist_file = f.name
    nx.write_edgelist(G, f, data=True)

# Read edge list
G_loaded = nx.read_edgelist(edgelist_file, data=True)

# Weighted edge list
with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".weighted") as f:
    weighted_file = f.name
    nx.write_weighted_edgelist(G, f)

G_weighted = nx.read_weighted_edgelist(weighted_file)
```

### Adjacency List Format

```python
# Write adjacency list
with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".adjlist") as f:
    adjlist_file = f.name
    nx.write_adjlist(G, f)

# Read adjacency list
G_adj = nx.read_adjlist(adjlist_file)
```

### GraphML Format (XML-based, preserves attributes)

```python
# Write GraphML
with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".graphml") as f:
    graphml_file = f.name
    nx.write_graphml(G, f)

# Read GraphML
G_graphml = nx.read_graphml(graphml_file)
```

### GML Format

```python
# Write GML
nx.write_gml(G, "graph.gml")

# Read GML
G_gml = nx.read_gml("graph.gml")
```

### GEXF Format (for Gephi visualization tool)

```python
# Write GEXF
with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".gexf") as f:
    gexf_file = f.name
    nx.write_gexf(G, f)

# Read GEXF
G_gexf = nx.read_gexf(gexf_file)
```

### Pickle Format (Python-specific, preserves all attributes)

```python
# Write pickle
with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".gpickle") as f:
    pickle_file = f.name
    nx.write_gpickle(G, f)

# Read pickle
G_pickle = nx.read_gpickle(pickle_file)
```

### Matrix Market Format

```python
import scipy as sp
import io

# Create complete graph
G = nx.complete_graph(5)
a = nx.to_numpy_array(G)

# Write to file in Matrix Market array format
fh = io.BytesIO()
sp.io.mmwrite(fh, a)

# Read from file
fh.seek(0)
H = nx.from_numpy_array(sp.io.mmread(fh))
```

### DOT Format (Graphviz)

```python
from networkx.drawing.nx_pydot import write_dot

# Write DOT file
write_dot(G, 'graph.dot')

# Use Graphviz layout
pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
nx.draw(G, pos=pos)
```

---

## Graph Conversions

### To/From NumPy Arrays

```python
import numpy as np

# Convert to adjacency matrix
adj_matrix = nx.to_numpy_array(G, weight="weight")
print("Adjacency matrix shape:", adj_matrix.shape)

# Create graph from adjacency matrix
G_from_matrix = nx.from_numpy_array(adj_matrix)

# With structured dtypes for multi-attribute edges
edges = [
    (0, 1, {"weight": 10, "cost": 2}),
    (1, 2, {"weight": 5, "cost": 100})
]
G = nx.Graph(edges)

# Create adjacency matrix with multiple attributes
dtype = np.dtype([("weight", float), ("cost", int)])
A = nx.to_numpy_array(G, dtype=dtype, weight=None)
print(A)
print(A["cost"])
```

### To/From Pandas DataFrames

```python
import pandas as pd

# Edge list DataFrame
df = nx.to_pandas_edgelist(G)
print(df.head())

# Create graph from DataFrame
G_from_df = nx.from_pandas_edgelist(df, edge_attr=True)

# With source and target columns specified
df = pd.DataFrame({
    'source': [1, 2, 3],
    'target': [2, 3, 1],
    'weight': [0.5, 1.0, 0.75]
})
G = nx.from_pandas_edgelist(df, source='source', target='target', 
                             edge_attr='weight')

# Adjacency DataFrame
adj_df = nx.to_pandas_adjacency(G)
print(adj_df)
```

### To/From Dictionaries

```python
# Dictionary of dictionaries
dict_of_dicts = nx.to_dict_of_dicts(G)
print(dict_of_dicts)

# Create graph from dict of dicts
G_from_dict = nx.from_dict_of_dicts(dict_of_dicts)

# Adjacency dictionary
for node, neighbors in dict_of_dicts.items():
    print(f"{node}: {neighbors}")
```

### To/From SciPy Sparse Matrices

```python
import scipy.sparse as sp

# Convert to sparse matrix
sparse_matrix = nx.to_scipy_sparse_array(G, weight='weight')

# Create graph from sparse matrix
G_from_sparse = nx.from_scipy_sparse_array(sparse_matrix)
```

---

## Advanced Topics

### Graph Views

Graph views provide a read-only view of a graph without copying data.

```python
# Create a view
H = G.copy(as_view=True)

# Subgraph view
subgraph = G.subgraph([1, 2, 3])  # View of nodes 1, 2, 3

# Edge subgraph view
edge_subgraph = G.edge_subgraph([(1, 2), (2, 3)])

# Reverse view (for directed graphs)
reversed_view = D.reverse(copy=False)
```

### MultiGraphs - Handling Parallel Edges

```python
M = nx.MultiGraph()

# Add multiple edges between same nodes
M.add_edge(1, 2, key="a", weight=1.0, type="road")
M.add_edge(1, 2, key="b", weight=2.0, type="rail")

# Count edges between nodes
print(M.number_of_edges(1, 2))  # 2

# Get all edges with keys
for u, v, key, data in M.edges(keys=True, data=True):
    print(f"{u}-{v} (key={key}): {data}")

# Get specific edge
print(M[1][2]["a"])  # {'weight': 1.0, 'type': 'road'}

# Weighted degree (sums across parallel edges)
print(dict(M.degree(weight='weight')))

# Convert to simple graph (keep min weight)
G = nx.Graph()
for n, nbrs in M.adjacency():
    for nbr, edict in nbrs.items():
        minvalue = min([d['weight'] for d in edict.values()])
        G.add_edge(n, nbr, weight=minvalue)
```

### Directed Graph Operations

```python
D = nx.DiGraph()
D.add_edges_from([(1, 2), (2, 3), (3, 1)])

# Check if directed
print(D.is_directed())  # True

# Convert to undirected
U = D.to_undirected()

# Reverse edges
R = D.reverse()

# Get edges in both directions
print(list(D.edges()))  # [(1, 2), (2, 3), (3, 1)]
print(list(R.edges()))  # [(2, 1), (3, 2), (1, 3)]
```

### Graph Copying

```python
# Shallow copy (structure copied, attributes shared)
H = G.copy()

# Deep copy (everything copied independently)
from copy import deepcopy
H = deepcopy(G)

# Copy and convert type
H = nx.DiGraph(G)  # Undirected to directed
U = nx.Graph(D)    # Directed to undirected
```

### Subgraphs

```python
# Node-induced subgraph
nodes_of_interest = [1, 2, 3, 4]
subgraph = G.subgraph(nodes_of_interest)

# Edge-induced subgraph
edges_of_interest = [(1, 2), (2, 3), (3, 4)]
edge_subgraph = G.edge_subgraph(edges_of_interest)

# Create copy (not view)
subgraph_copy = G.subgraph(nodes_of_interest).copy()
```

### Graph Operators

```python
# Union
H = nx.union(G1, G2)

# Intersection
H = nx.intersection(G1, G2)

# Difference
H = nx.difference(G1, G2)

# Symmetric difference
H = nx.symmetric_difference(G1, G2)

# Compose (overlay G2 on G1)
H = nx.compose(G1, G2)

# Disjoint union
H = nx.disjoint_union(G1, G2)

# Cartesian product
H = nx.cartesian_product(G1, G2)
```

### Blockmodels and Quotient Graphs

```python
# Create blockmodel by partitioning nodes
from collections import defaultdict
import scipy as sp

def create_hc(G):
    """Creates hierarchical cluster from distance matrix"""
    path_length = nx.all_pairs_shortest_path_length(G)
    distances = np.zeros((len(G), len(G)))
    for u, p in path_length:
        for v, d in p.items():
            distances[u][v] = d
    
    Y = sp.spatial.distance.squareform(distances)
    Z = sp.cluster.hierarchy.complete(Y)
    membership = list(sp.cluster.hierarchy.fcluster(Z, t=1.15))
    
    partition = defaultdict(list)
    for n, p in zip(list(range(len(G))), membership):
        partition[p].append(n)
    return list(partition.values())

# Create partitions
partitions = create_hc(G)

# Build blockmodel (quotient graph)
BM = nx.quotient_graph(G, partitions, relabel=True)
```

---

## Best Practices

### Performance Tips

1. **Choose the right graph type:**
   - Use `Graph` for simple undirected graphs
   - Use `DiGraph` only when direction matters
   - Avoid `MultiGraph` unless parallel edges needed

2. **Iterate efficiently:**
   ```python
   # Good - direct access
   for node in G:
       neighbors = G[node]
   
   # Avoid - unnecessary conversions
   for node in list(G.nodes()):
       neighbors = list(G.neighbors(node))
   ```

3. **Use views instead of copies:**
   ```python
   # View (fast, no memory overhead)
   subgraph = G.subgraph([1, 2, 3])
   
   # Copy (slower, more memory)
   subgraph = G.subgraph([1, 2, 3]).copy()
   ```

4. **Batch operations:**
   ```python
   # Good
   G.add_nodes_from(range(1000))
   G.add_edges_from(edge_list)
   
   # Bad
   for i in range(1000):
       G.add_node(i)
   ```

5. **Use appropriate algorithms:**
   - BFS for unweighted shortest paths
   - Dijkstra for weighted shortest paths (non-negative)
   - Bellman-Ford for negative weights

### Memory Management

```python
# Clear unnecessary data
G.clear_edges()  # Keep nodes, remove edges
G.clear()        # Remove everything

# Use generators when possible
# Good
paths = nx.all_shortest_paths(G, source, target)
for path in paths:
    process(path)

# Less memory efficient
all_paths = list(nx.all_shortest_paths(G, source, target))
```

### Error Handling

```python
try:
    path = nx.shortest_path(G, source, target)
except nx.NetworkXNoPath:
    print("No path exists between nodes")

try:
    is_planar, embedding = nx.check_planarity(G)
except nx.NetworkXException as e:
    print(f"Error: {e}")
```

### Graph Validation

```python
# Check if graph is valid for algorithm
if not nx.is_connected(G):
    # Work with largest component
    largest_cc = max(nx.connected_components(G), key=len)
    G = G.subgraph(largest_cc).copy()

# For directed algorithms
if not D.is_directed():
    D = D.to_directed()

# Check for DAG
if not nx.is_directed_acyclic_graph(D):
    print("Graph contains cycles")
```

### Documentation and Type Hints

```python
from typing import Dict, Set, List
import networkx as nx

def analyze_network(G: nx.Graph) -> Dict[str, float]:
    """
    Analyze network properties.
    
    Args:
        G: NetworkX graph to analyze
        
    Returns:
        Dictionary with network metrics
    """
    metrics = {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'avg_clustering': nx.average_clustering(G)
    }
    return metrics
```

### Testing

```python
# Create test graphs
G_empty = nx.Graph()
G_single = nx.Graph()
G_single.add_node(1)
G_path = nx.path_graph(5)
G_complete = nx.complete_graph(5)

# Assertions
assert G.number_of_nodes() == 5
assert G.has_edge(1, 2)
assert nx.is_connected(G)
```

---

## Example: Complete Workflow

```python
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# 1. Create graph
G = nx.karate_club_graph()

# 2. Analyze structure
print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
print(f"Density: {nx.density(G):.3f}")
print(f"Average clustering: {nx.average_clustering(G):.3f}")

# 3. Identify communities
communities = list(nx.community.greedy_modularity_communities(G))
modularity = nx.community.modularity(G, communities)
print(f"Communities: {len(communities)}, Modularity: {modularity:.3f}")

# 4. Calculate centrality
betweenness = nx.betweenness_centrality(G)
degree_cent = nx.degree_centrality(G)

# 5. Find most important nodes
top_nodes = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
print("Top 5 nodes by betweenness:")
for node, score in top_nodes:
    print(f"  Node {node}: {score:.3f}")

# 6. Visualize
community_map = {node: i for i, comm in enumerate(communities) for node in comm}
pos = nx.spring_layout(G, seed=42, k=0.5)

node_colors = [community_map[node] for node in G.nodes()]
node_sizes = [3000 * betweenness[node] + 100 for node in G.nodes()]

plt.figure(figsize=(14, 10))
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                       cmap=plt.cm.Set3, alpha=0.8)
nx.draw_networkx_edges(G, pos, alpha=0.3)
nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold")

plt.title("Karate Club Network - Size by Centrality, Color by Community", 
          fontsize=16, fontweight="bold")
plt.axis("off")
plt.tight_layout()
plt.savefig("karate_analysis.png", dpi=300, bbox_inches="tight")
plt.show()

# 7. Export results
nx.write_gml(G, "karate_club.gml")
print("\nGraph saved to karate_club.gml")
```

---

## Resources

### Official Documentation
- **NetworkX Documentation:** https://networkx.org/documentation/stable/
- **Tutorial:** https://networkx.org/documentation/stable/tutorial.html
- **Reference:** https://networkx.org/documentation/stable/reference/index.html
- **Gallery:** https://networkx.org/documentation/stable/auto_examples/index.html

### Books and Papers
- **"Complex Network Analysis in Python"** by Dmitry Zinoviev
- **"Network Science"** by Albert-László Barabási (free online)
- Original NetworkX paper: "Exploring network structure, dynamics, and function using NetworkX"

### Community
- **GitHub:** https://github.com/networkx/networkx
- **Stack Overflow:** Tag `networkx`
- **Discussions:** https://github.com/networkx/networkx/discussions

### Related Libraries
- **graph-tool:** High-performance graph analysis
- **igraph:** Fast graph library with Python interface
- **Gephi:** Interactive visualization platform
- **Cytoscape:** Network visualization and analysis platform

---

## Quick Reference Card

```python
# Create
G = nx.Graph()                              # Undirected
D = nx.DiGraph()                            # Directed
M = nx.MultiGraph()                         # Multigraph

# Add elements
G.add_node(1, attr=value)                  # Single node
G.add_nodes_from([2, 3])                   # Multiple nodes
G.add_edge(1, 2, weight=4.7)               # Single edge
G.add_edges_from([(1, 2), (2, 3)])         # Multiple edges

# Access
G.nodes()                                   # All nodes
G.edges()                                   # All edges
G[1]                                        # Neighbors of 1
G.degree(1)                                 # Degree of 1
G.neighbors(1)                              # Iterator over neighbors

# Analyze
nx.shortest_path(G, source, target)        # Shortest path
nx.betweenness_centrality(G)               # Betweenness
nx.connected_components(G)                 # Components
nx.density(G)                              # Density
nx.clustering(G)                           # Clustering coef

# Generate
G = nx.complete_graph(5)                   # Complete graph
G = nx.path_graph(10)                      # Path graph
G = nx.erdos_renyi_graph(100, 0.05)        # Random graph
G = nx.barabasi_albert_graph(100, 2)       # Scale-free

# I/O
nx.write_gml(G, "file.gml")                # Write
G = nx.read_gml("file.gml")                # Read
nx.write_graphml(G, "file.graphml")        # GraphML
nx.to_numpy_array(G)                       # NumPy array
nx.to_pandas_edgelist(G)                   # Pandas DataFrame

# Visualize
nx.draw(G, with_labels=True)               # Basic draw
pos = nx.spring_layout(G)                  # Layout
nx.draw(G, pos, node_color='red')          # Custom
plt.savefig("graph.png")                   # Save
```

---

*This reference guide covers NetworkX 3.0+. For the most up-to-date information, visit https://networkx.org/*
