"""
Graph Memory.

Interface to Neo4j for storing entities and relationships as a knowledge graph.
Provides structured traversal and relational queries over the knowledge base.
"""

from neo4j import AsyncGraphDatabase

from backend.config.settings import get_settings
from backend.models.knowledge import Entity, KnowledgeEdge, KnowledgeNode


class GraphMemory:
    """Store and query knowledge nodes and edges in Neo4j."""

    def __init__(self) -> None:
        settings = get_settings()
        self._driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    async def close(self) -> None:
        """Close the Neo4j driver connection."""
        await self._driver.close()

    async def store_entity(self, entity: Entity) -> None:
        """Upsert an entity node into the graph.

        Args:
            entity: The entity to store.
        """
        async with self._driver.session() as session:
            await session.run(
                """
                MERGE (e:Entity {name: $name, entity_type: $entity_type})
                SET e.chunk_id = $chunk_id
                """,
                name=entity.name,
                entity_type=entity.entity_type,
                chunk_id=str(entity.chunk_id),
            )

    async def store_node(self, node: KnowledgeNode) -> None:
        """Upsert a generic knowledge node into the graph.

        Args:
            node: The knowledge node to store.
        """
        async with self._driver.session() as session:
            await session.run(
                """
                MERGE (n:KnowledgeNode {id: $id})
                SET n.label = $label, n.node_type = $node_type
                """,
                id=str(node.id),
                label=node.label,
                node_type=node.node_type,
            )

    async def store_edge(self, edge: KnowledgeEdge) -> None:
        """Create a directed relationship between two knowledge nodes.

        Args:
            edge: The edge describing the relationship.
        """
        async with self._driver.session() as session:
            await session.run(
                """
                MATCH (a:KnowledgeNode {id: $source_id})
                MATCH (b:KnowledgeNode {id: $target_id})
                MERGE (a)-[r:RELATES {relation: $relation}]->(b)
                SET r.weight = $weight
                """,
                source_id=str(edge.source_id),
                target_id=str(edge.target_id),
                relation=edge.relation,
                weight=edge.weight,
            )

    async def get_all_nodes(self) -> list[dict]:
        """Return all knowledge nodes in the graph.

        Returns:
            List of node property dictionaries.
        """
        async with self._driver.session() as session:
            result = await session.run("MATCH (n:KnowledgeNode) RETURN n")
            return [record["n"]._properties async for record in result]
