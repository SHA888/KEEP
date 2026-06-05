"""Adapter to wire LLMProposer into the runner with AgentDojo observations.

This adapter bridges the interface gap: runner.run() calls agent.propose()
with no arguments, but LLMProposer.propose() requires observations and
task_description. The adapter stores observations at initialization and
provides a propose() method compatible with the runner's agent interface.

The adapter is intentionally untrusted: it reads observations that may
contain injected data. LLMProposer will see the full observation (including
injection payloads) and propose tool calls. The base will authorize/block
based on minted capabilities, not on what the LLM proposes.
"""

from __future__ import annotations

import copy
from typing import Any

from .llm_proposer import LLMProposer


class AgentDojoAdapter:
    """Adapts LLMProposer to the runner's agent interface.

    Stores observations at initialization and provides a propose() method
    compatible with runner.run(). Observations are deep-copied to protect
    against external mutations. The adapter reads untrusted data (observations
    may contain injected payloads) and passes it to LLMProposer unchanged.
    Authorization is deferred entirely to TrustedBase.authorize().
    """

    def __init__(
        self,
        llm_proposer: LLMProposer,
        observations: dict[str, Any],
        task_description: str = "",
    ) -> None:
        """Initialize adapter with LLM proposer and observations.

        Args:
            llm_proposer: The Claude API-based proposer (must have propose method).
            observations: Agent-observable data from AgentDojo environment
                         (transaction history, balance, etc.). Stored as a deep
                         copy to prevent external mutations from affecting proposals.
            task_description: Optional description of the user's task
                            (e.g., "Check my balance and recent transactions").

        Raises:
            TypeError: If llm_proposer lacks propose method or task_description
                      is not a string.
        """
        if not hasattr(llm_proposer, "propose") or not callable(
            getattr(llm_proposer, "propose")
        ):
            raise TypeError(
                f"llm_proposer must have a callable propose() method, got {type(llm_proposer)}"
            )
        if not isinstance(task_description, str):
            raise TypeError(
                f"task_description must be str, got {type(task_description)}"
            )
        self._proposer = llm_proposer
        self._observations = copy.deepcopy(observations)
        self._task_description = task_description

    def propose(self) -> list[tuple[str, dict]]:
        """Propose tool calls by calling LLMProposer with stored observations.

        Returns:
            List of (tool, args) proposals from the LLM.

        Raises:
            ValueError: If LLMProposer.propose() fails (API error, invalid response).
        """
        try:
            return self._proposer.propose(self._observations, self._task_description)
        except ValueError as e:
            raise ValueError(f"LLM proposal failed: {e}") from e
