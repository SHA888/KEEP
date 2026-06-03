"""The untrusted neural component.

In the P0 probe this is a stub that can be made to propose ANYTHING — including
exactly the attacker's action — because the whole point is that the guarantee does
not depend on the model behaving. In P2 this is replaced by a real LLM; the base
above it does not change.
"""
from __future__ import annotations


class UntrustedAgent:
    def __init__(self, proposals: list[tuple[str, dict]]) -> None:
        # Each proposal is a (tool, args) call the "model" emits — possibly
        # attacker-controlled, since it may be produced over untrusted input.
        self._proposals = proposals

    def propose(self) -> list[tuple[str, dict]]:
        return list(self._proposals)
