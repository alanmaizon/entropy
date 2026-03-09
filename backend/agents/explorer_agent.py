"""
Explorer Agent.

Generates hypotheses and explores the knowledge space by querying memory
and proposing new ideas for the CriticAgent to evaluate.
"""

from backend.agents.base_agent import AgentMessage, BaseAgent
from backend.reasoning.hypothesis_generator import HypothesisGenerator


class ExplorerAgent(BaseAgent):
    """Generates hypotheses from memory for a given topic."""

    name = "explorer"

    def __init__(self) -> None:
        self._generator = HypothesisGenerator()

    async def run(self, message: AgentMessage) -> AgentMessage:
        """Generate a hypothesis for the topic in the incoming message.

        Args:
            message: Must contain ``content["topic"]`` as a string.

        Returns:
            A message with ``content["hypothesis"]`` containing the
            serialised :class:`~backend.models.hypothesis.Hypothesis`.
        """
        topic = message.content.get("topic", "")
        hypothesis = await self._generator.generate(topic)
        return AgentMessage(
            sender=self.name,
            recipient=message.sender,
            content={"hypothesis": hypothesis.model_dump(mode="json")},
        )
