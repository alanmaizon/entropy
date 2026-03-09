"""Planner Agent.

Schedules and coordinates reasoning cycles. Decides which topics to
explore next based on the current state of episodic memory and the
knowledge graph.
"""

from backend.agents.base_agent import AgentMessage, BaseAgent
from backend.memory.episodic_memory import EpisodicMemory
from backend.models.hypothesis import HypothesisStatus


class PlannerAgent(BaseAgent):
    """Plans reasoning cycles and prioritises topics for exploration."""

    name = "planner"

    def __init__(self, episodic: EpisodicMemory | None = None) -> None:
        self._episodic = episodic or EpisodicMemory(db_path=":memory:")

    async def run(self, message: AgentMessage) -> AgentMessage:
        """Determine next actions based on the current knowledge state.

        Accepts messages with:
            - ``content["action"] == "plan"``: returns topics to explore
            - ``content["action"] == "status"``: returns system status

        Args:
            message: The incoming request.

        Returns:
            A message with planning recommendations.
        """
        action = message.content.get("action", "plan")

        if action == "status":
            return await self._status(message)
        return await self._plan(message)

    async def _plan(self, message: AgentMessage) -> AgentMessage:
        """Suggest what the system should do next."""
        episodes = self._episodic.get_all()
        uncertain = self._episodic.get_by_status(HypothesisStatus.UNCERTAIN.value)
        pending = self._episodic.get_by_status(HypothesisStatus.PENDING.value)

        recommendations = []
        if uncertain or pending:
            recommendations.append({
                "action": "revisit",
                "count": len(uncertain) + len(pending),
                "reason": "Uncertain/pending hypotheses need re-evaluation",
            })

        # Suggest exploring the original topic further if provided
        topic = message.content.get("topic", "")
        if topic:
            recommendations.append({
                "action": "explore",
                "topic": topic,
                "reason": "Continue exploring the requested topic",
            })

        return AgentMessage(
            sender=self.name,
            recipient=message.sender,
            content={
                "recommendations": recommendations,
                "total_episodes": len(episodes),
            },
        )

    async def _status(self, message: AgentMessage) -> AgentMessage:
        """Return a summary of the system's current episodic state."""
        episodes = self._episodic.get_all()
        accepted = self._episodic.get_by_status(HypothesisStatus.ACCEPTED.value)
        rejected = self._episodic.get_by_status(HypothesisStatus.REJECTED.value)
        uncertain = self._episodic.get_by_status(HypothesisStatus.UNCERTAIN.value)

        return AgentMessage(
            sender=self.name,
            recipient=message.sender,
            content={
                "total": len(episodes),
                "accepted": len(accepted),
                "rejected": len(rejected),
                "uncertain": len(uncertain),
            },
        )
