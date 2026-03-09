"""Agents package.

Implements a multi-agent reasoning system with message-passing coordination:

- ExplorerAgent: generates hypotheses and ideas from memory.
- CriticAgent: evaluates logical consistency and evidence support.
- ResearchAgent: finds supporting information from memory.
- PlannerAgent: schedules reasoning cycles and prioritises exploration.
- MessageBus: routes messages between agents.

Agents communicate via structured Pydantic messages through the MessageBus.
"""
