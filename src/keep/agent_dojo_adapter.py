"""Adapter to wire LLMProposer into the runner with AgentDojo observations.

This adapter bridges the interface gap:
- runner.run() calls agent.propose() with no arguments
- LLMProposer.propose() requires observations and task_description

The adapter stores observations at initialization time and provides a
propose() method compatible with the runner interface.
"""

from __future__ import annotations

from typing import Any

from .llm_proposer import LLMProposer


class AgentDojoAdapter:
    """Adapts LLMProposer to the runner's agent interface.

    The runner expects an agent with propose() method that takes no arguments.
    This adapter stores observations (from AgentDojo environment) and returns
    proposals from LLMProposer when propose() is called.

    The adapter is intentionally untrusted: it reads observations that may
    contain injected data. LLMProposer will see the full observation (including
    injection payloads) and propose tool calls. The base will authorize/block
    based on minted capabilities, not on what the LLM proposes.
    """

    def __init__(
        self,
        llm_proposer: LLMProposer,
        observations: dict[str, Any],
        task_description: str = "",
    ) -> None:
        """Initialize adapter with LLM proposer and observations.

        Args:
            llm_proposer: The Claude API-based proposer.
            observations: Agent-observable data from AgentDojo environment
                         (transaction history, balance, etc.).
                         May contain injected payloads — adapter does not sanitize.
            task_description: Optional description of the user's task
                            (e.g., "Check my balance and recent transactions").
        """
        self._proposer = llm_proposer
        self._observations = observations
        self._task_description = task_description

    def propose(self) -> list[tuple[str, dict]]:
        """Propose tool calls by calling LLMProposer with stored observations.

        Returns:
            List of (tool, args) proposals from the LLM.

        Note: The adapter passes observations to the LLM without sanitization.
        If observations contain injection payloads, the LLM will see them.
        The base is responsible for authorizing only calls within minted capabilities.
        """
        return self._proposer.propose(self._observations, self._task_description)
