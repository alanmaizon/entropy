"""
Base Agent.

Abstract base class for all agents in the Enthropy system.
Agents share a common message-passing interface.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class AgentMessage(BaseModel):
    """A structured message passed between agents."""

    sender: str
    recipient: str
    content: dict[str, Any]


class BaseAgent(ABC):
    """Abstract agent with a name and a run method."""

    name: str = "base"

    @abstractmethod
    async def run(self, message: AgentMessage) -> AgentMessage:
        """Process an incoming message and return a response message.

        Args:
            message: The incoming :class:`AgentMessage`.

        Returns:
            A response :class:`AgentMessage`.
        """
