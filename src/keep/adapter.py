"""Adapter — AgentDojo scenario -> KEEP deriver input.

This module converts AgentDojo's user tasks (free-form or scenario-specific) into
KEEP's structured trusted instruction format that the deriver can mint capabilities from.

For P0, this handles the banking-suite scenario only: extracting the rent-payment task
and structuring it as a deriver-compatible dict.

Design note: This adapter is part of the *trusted* instruction channel (per UNTRUST §12).
As the deriver is widened to handle more scenarios (P1+), this adapter's responsibility
grows. For now, it is intentionally narrow and scenario-specific.

The adapter also bridges AgentDojo tool proposals to capability scope constraints
by validating tool calls against the known tool schema.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from .tool_schema import validate_tool_call, scope_for_tool, BANKING_TOOLS


@dataclass
class TrustedInstruction:
    """Structured trusted instruction for the deriver."""

    action: str
    to: str
    amount: float


def adapt_banking_scenario(
    user_task: str, scenario_context: dict | None = None
) -> TrustedInstruction:
    """Adapt AgentDojo banking-scenario user task to KEEP deriver input format.

    Args:
        user_task: Free-form user task string (e.g., "Pay my rent of $1500 to landlord@example.com")
        scenario_context: Optional context from the scenario (e.g., from THREAT.md scenario definition)

    Returns:
        TrustedInstruction dict-compatible object with action, to, amount.

    Raises:
        ValueError: If task cannot be parsed to a valid instruction.
    """
    # For P0 banking scenario: extract rent-payment task
    # Input: "Pay my rent of $1500 to landlord@example.com"
    # Output: TrustedInstruction(action="pay_rent", to="landlord@example.com", amount=1500)

    user_task_lower = user_task.lower()

    # Detect rent-payment task
    if "rent" in user_task_lower and "pay" in user_task_lower:
        # Extract amount (look for currency amounts, handle variable decimal places)
        amount_match = re.search(r"\$?(\d+(?:,\d{3})*(?:\.\d+)?)", user_task)
        if not amount_match:
            raise ValueError(f"Cannot extract amount from task: {user_task}")
        amount = float(amount_match.group(1).replace(",", ""))

        # Extract recipient (look for email or "landlord")
        # For P0, hardcode the landlord recipient from THREAT.md scenario
        recipient = "landlord@example.com"
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", user_task)
        if email_match:
            recipient = email_match.group(0)

        return TrustedInstruction(action="pay_rent", to=recipient, amount=amount)

    raise ValueError(
        f"Unrecognized task format (P0 supports rent-payment only): {user_task}"
    )


def trusted_instruction_to_deriver_input(instruction: TrustedInstruction) -> dict:
    """Convert TrustedInstruction to deriver.derive() input format.

    Args:
        instruction: TrustedInstruction object

    Returns:
        Dict compatible with deriver.derive(user_task: dict)
    """
    return {
        "action": instruction.action,
        "to": instruction.to,
        "amount": instruction.amount,
    }


def validate_agentdojo_tool_call(tool: str, args: dict) -> tuple[bool, str | None]:
    """Validate an AgentDojo tool call against the known tool schema.

    This is the public adapter API for tool-call validation (UNTRUST §12 seam).
    It bridges untrusted agent proposals to trusted schema validation.
    Any tool call that doesn't match the schema is rejected outright.

    Args:
        tool: Tool name as proposed by AgentDojo
        args: Tool arguments as proposed by AgentDojo

    Returns:
        (is_valid, error_message)
    """
    return validate_tool_call(tool, args)


def capability_scope_for_tool_call(
    tool: str, args: dict
) -> tuple[tuple[str, object], ...]:
    """Generate capability scope constraints for a tool call.

    This is the public adapter API for scope generation (UNTRUST §12 seam).
    It ensures that when a capability is minted for this tool call,
    it includes all required parameters to prevent injection attacks.
    A call with different parameter values cannot match the minted scope.

    Args:
        tool: Tool name (assumed validated)
        args: Tool arguments (assumed validated)

    Returns:
        Scope constraints as (param_name, value) tuples
    """
    return scope_for_tool(tool, args)


def list_available_tools() -> list[str]:
    """List all tools available in the current scenario (AgentDojo banking suite).

    For P0, returns the banking suite tools. As scenarios expand (P1+), this
    function grows to enumerate all available tools across all active scenarios.

    Returns:
        List of tool names
    """
    return [schema.name for schema in BANKING_TOOLS]
