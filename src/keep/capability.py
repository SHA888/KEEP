"""Capability — an unforgeable authorization to perform one scoped operation.

In this probe, unforgeability is enforced structurally: the trusted base holds the
only registry of live capabilities, and the untrusted agent never receives a token
it could forge — it only *proposes* (tool, args) calls that the base checks against
its registry. Cryptographic signing (real Sketch 4) is a later step; the structural
guarantee in a single-process probe does not depend on it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    """Authorizes `tool` calls whose args match every constraint in `scope`.

    `scope` is a tuple of (arg_name, required_value) pairs — frozen so the
    capability is hashable and immutable once minted.

    `renewal` is the number of times this capability can be used. For single-step
    tasks, renewal defaults to 1 (one-shot). For multi-step tasks, renewal can be
    set higher to allow reuse across steps. Renewal is consumed (decremented) on
    each authorization that matches this capability.
    """

    tool: str
    scope: tuple[tuple[str, object], ...]
    nonce: str
    renewal: int = 1

    def authorizes(self, tool: str, args: dict) -> bool:
        if tool != self.tool:
            return False
        # Every constrained arg must be present and exactly equal.
        return all(args.get(key) == value for key, value in self.scope)
