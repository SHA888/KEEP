"""Deriver — trusted user instruction -> capability set.

This function IS the labeling / autoformalisation seam (UNTRUST §12). For the probe
it is intentionally narrow and deterministic: it consumes a *structured* trusted task,
not free-form natural language, so the seam is small and auditable. Widening it to
parse free NL is exactly where the guarantee gets harder — that is the honest research
edge, deliberately not papered over here.

The deriver uses tool_schema to ensure that scope constraints are tight and match
the available tools' parameter definitions.
"""
from __future__ import annotations

import itertools

from .capability import Capability
from .tool_schema import get_tool_schema, scope_for_tool

_counter = itertools.count()


def derive(user_task: dict) -> list[Capability]:
    """Mint capabilities from a trusted, structured user task.

    Example task: {"action": "pay_rent", "to": "landlord@example.com", "amount": 1500}
    -> one capability: send_money scoped to exactly that recipient and amount.

    Scope constraints are generated using the tool schema to ensure they match
    the tool's parameter definitions (UNTRUST §12 seam protection).
    """
    caps: list[Capability] = []
    if user_task.get("action") == "pay_rent":
        # Map action to tool and build args for scope generation
        tool = "send_money"
        args = {
            "to": user_task["to"],
            "amount": user_task["amount"],
        }

        # Validate that this tool exists and args are in schema
        schema = get_tool_schema(tool)
        if schema is not None:
            is_valid, _ = schema.validate_args(args)
            if is_valid:
                # Generate scope constraints from tool schema
                scope = scope_for_tool(tool, args)
                caps.append(
                    Capability(
                        tool=tool,
                        scope=scope,
                        nonce=f"cap-{next(_counter)}",
                    )
                )
    return caps
