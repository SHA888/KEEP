"""The trusted base. Deliberately small and auditable. No LLM in its trust path.

This is the whole trusted computing base of the probe: a capability registry, an
authorization check, and an audit log. Everything else (the model, the deriver's
input) is untrusted or a named seam (see THREAT.md).
"""
from __future__ import annotations

from typing import Callable

from .capability import Capability


class Unauthorized(Exception):
    """Raised when a proposed call matches no minted capability."""


class TrustedBase:
    def __init__(self) -> None:
        self._caps: list[Capability] = []
        self.audit: list[tuple] = []

    def mint(self, cap: Capability) -> None:
        """Register a capability.

        Invariant the probe depends on: `mint` is called ONLY by the deriver, ONLY
        from the trusted user-instruction channel — never from agent output derived
        over untrusted data. (The coercion path, UNTRUST §7, lives at this line.)
        """
        self._caps.append(cap)
        self.audit.append(("mint", cap.tool, cap.scope))

    def authorize(self, tool: str, args: dict) -> bool:
        ok = any(cap.authorizes(tool, args) for cap in self._caps)
        self.audit.append(("authorize", tool, args, ok))
        return ok

    def execute(self, tool: str, args: dict, effect: Callable[[str, dict], object]):
        """Execute `effect` only if some minted capability authorizes the call."""
        if not self.authorize(tool, args):
            self.audit.append(("BLOCKED", tool, args))
            raise Unauthorized(f"No capability authorizes {tool}{args}")
        return effect(tool, args)
