"""
FastAPI dependency injection providers.

Centralises creation of shared service/memory instances so they can be
easily swapped out in tests.
"""

from functools import lru_cache

from backend.memory.episodic_memory import EpisodicMemory
from backend.memory.graph_memory import GraphMemory
from backend.memory.vector_memory import VectorMemory
from backend.reasoning.critic_evaluator import CriticEvaluator
from backend.reasoning.hypothesis_generator import HypothesisGenerator
from backend.reasoning.knowledge_updater import KnowledgeUpdater


@lru_cache
def get_vector_memory() -> VectorMemory:
    return VectorMemory()


@lru_cache
def get_graph_memory() -> GraphMemory:
    return GraphMemory()


@lru_cache
def get_episodic_memory() -> EpisodicMemory:
    return EpisodicMemory()


@lru_cache
def get_hypothesis_generator() -> HypothesisGenerator:
    return HypothesisGenerator()


@lru_cache
def get_critic_evaluator() -> CriticEvaluator:
    return CriticEvaluator()


@lru_cache
def get_knowledge_updater() -> KnowledgeUpdater:
    return KnowledgeUpdater()
