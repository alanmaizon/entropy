"""Message Bus.

Lightweight publish-subscribe message bus for agent communication.
Agents register themselves and send messages via the bus rather than
calling each other directly.
"""

from __future__ import annotations

import logging
from collections import defaultdict

from backend.agents.base_agent import AgentMessage, BaseAgent

logger = logging.getLogger(__name__)


class MessageBus:
    """In-process message bus for agent-to-agent communication.

    Agents register by name. Messages are routed to the named recipient.
    Supports broadcast to all agents and topic-based subscriptions.
    """

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self._log: list[AgentMessage] = []

    def register(self, agent: BaseAgent) -> None:
        """Register an agent on the bus.

        Args:
            agent: The agent to register. Must have a unique ``name``.
        """
        self._agents[agent.name] = agent
        logger.info("Agent registered: %s", agent.name)

    def registered_agents(self) -> list[str]:
        """Return the names of all registered agents."""
        return list(self._agents.keys())

    async def send(self, message: AgentMessage) -> AgentMessage:
        """Send a message to a specific agent and return its response.

        Args:
            message: The message to deliver. ``recipient`` must match
                a registered agent name.

        Returns:
            The agent's response message.

        Raises:
            KeyError: If the recipient agent is not registered.
        """
        if message.recipient not in self._agents:
            raise KeyError(
                f"Agent '{message.recipient}' not registered. "
                f"Available: {self.registered_agents()}"
            )

        self._log.append(message)
        logger.info(
            "Message: %s -> %s", message.sender, message.recipient
        )

        agent = self._agents[message.recipient]
        response = await agent.run(message)
        self._log.append(response)
        return response

    async def broadcast(self, message: AgentMessage) -> list[AgentMessage]:
        """Send a message to all registered agents (except the sender).

        Args:
            message: The message to broadcast.

        Returns:
            List of response messages from all agents.
        """
        responses = []
        for name, agent in self._agents.items():
            if name == message.sender:
                continue
            msg = message.model_copy(update={"recipient": name})
            response = await agent.run(msg)
            self._log.append(msg)
            self._log.append(response)
            responses.append(response)
        return responses

    def get_log(self) -> list[AgentMessage]:
        """Return the full message log for observability."""
        return list(self._log)
