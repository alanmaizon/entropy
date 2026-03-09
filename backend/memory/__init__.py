"""
Memory package.

Implements a hybrid memory architecture combining:
- Vector memory  (Qdrant) – semantic similarity search
- Graph memory   (Neo4j)  – relational knowledge storage
- Episodic memory (in-process list) – hypothesis evaluation log
"""
