"""Deriver — trusted user instruction -> capability set.

This function IS the labeling / autoformalisation seam (UNTRUST §12). For the probe
it is intentionally narrow and deterministic: it consumes a *structured* trusted task,
not free-form natural language, so the seam is small and auditable. Widening it to
parse free NL is exactly where the guarantee gets harder — that is the honest research
edge, deliberately not papered over here.
"""
from __future__ import annotations

import itertools

from .capability import Capability

_counter = itertools.count()


def derive(user_task: dict) -> list[Capability]:
    """Mint capabilities from a trusted, structured user task.

    Example task: {"action": "pay_rent", "to": "landlord@example.com", "amount": 1500}
    -> one capability: send_money scoped to exactly that recipient and amount.
    """
    caps: list[Capability] = []
    if user_task.get("action") == "pay_rent":
        caps.append(
            Capability(
                tool="send_money",
                scope=(("to", user_task["to"]), ("amount", user_task["amount"])),
                nonce=f"cap-{next(_counter)}",
            )
        )
    return caps
