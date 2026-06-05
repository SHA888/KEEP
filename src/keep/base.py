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
        self._caps: list[dict] = []  # Each element: {"cap": Capability, "renewal": int}
        self.audit: list[tuple] = []

    def mint(self, cap: Capability) -> None:
        """Register a capability.

        Invariant the probe depends on: `mint` is called ONLY by the deriver, ONLY
        from the trusted user-instruction channel — never from agent output derived
        over untrusted data. (The coercion path, UNTRUST §7, lives at this line.)
        """
        self._caps.append({"cap": cap, "renewal": cap.renewal})
        self.audit.append(("mint", cap.tool, cap.scope, cap.renewal))

    def authorize(self, tool: str, args: dict) -> bool:
        """Check if any minted capability authorizes this call and has renewal remaining.

        If a matching capability is found AND has renewal > 0, decrement its renewal
        (consume it for one use) and return True. This enforces the capability lifecycle
        for multi-step scenarios: capabilities are consumed as they are used.

        Audit tuple format (consistent across success and failure):
        - Success: ("authorize", tool, args, True, nonce, renewal_after)
        - Failure: ("authorize", tool, args, False, None, None)
        """
        for entry in self._caps:
            cap = entry["cap"]
            if cap.authorizes(tool, args) and entry["renewal"] > 0:
                # Found a matching capability with remaining renewals
                entry["renewal"] -= 1
                self.audit.append(
                    ("authorize", tool, args, True, cap.nonce, entry["renewal"])
                )
                return True
        # No matching capability with renewal remaining
        self.audit.append(("authorize", tool, args, False, None, None))
        return False

    def execute(self, tool: str, args: dict, effect: Callable[[str, dict], object]):
        """Execute `effect` only if some minted capability authorizes the call."""
        if not self.authorize(tool, args):
            self.audit.append(("BLOCKED", tool, args))
            raise Unauthorized(f"No capability authorizes {tool}{args}")
        return effect(tool, args)
