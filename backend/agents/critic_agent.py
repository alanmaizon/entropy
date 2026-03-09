"""
Critic Agent.

Evaluates hypotheses produced by the ExplorerAgent, assigning confidence
scores and verdicts based on evidence retrieved from memory.
"""

from backend.agents.base_agent import AgentMessage, BaseAgent
from backend.models.hypothesis import Hypothesis
from backend.reasoning.critic_evaluator import CriticEvaluator


class CriticAgent(BaseAgent):
    """Evaluates hypotheses and returns scored critique results."""

    name = "critic"

    def __init__(self) -> None:
        self._evaluator = CriticEvaluator()

    async def run(self, message: AgentMessage) -> AgentMessage:
        """Evaluate the hypothesis contained in the incoming message.

        Args:
            message: Must contain ``content["hypothesis"]`` as a dict.

        Returns:
            A message with ``content["critique"]`` containing the
            serialised :class:`~backend.models.hypothesis.CritiqueResult`.
        """
        hypothesis = Hypothesis(**message.content["hypothesis"])
        critique = await self._evaluator.evaluate(hypothesis)
        return AgentMessage(
            sender=self.name,
            recipient=message.sender,
            content={"critique": critique.model_dump(mode="json")},
        )
