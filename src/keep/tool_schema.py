"""Tool schema — AgentDojo tool definitions and validation.

This module defines the schema for all available tools in the AgentDojo banking suite.
It serves as the interface between untrusted tool proposals (from AgentDojo) and the
trusted base, ensuring that:
1. Proposed tool calls match known schemas (no injection of unknown tools)
2. Capabilities minted for each tool include all necessary scope constraints
3. The seam is small and auditable (UNTRUST §12)

For P0, this is the banking suite only. As the deriver widens (P1+), tool definitions
grow; the schema remains the source of truth for valid parameter names.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolParameter:
    """Definition of one tool parameter."""
    name: str
    required: bool = True


@dataclass(frozen=True)
class ToolSchema:
    """Definition of one tool: its name and required parameters."""
    name: str
    parameters: tuple[ToolParameter, ...]

    def validate_args(self, args: dict) -> tuple[bool, str | None]:
        """Check if args conform to this schema.

        Returns (is_valid, error_message).
        """
        # All required parameters must be present
        required_names = {p.name for p in self.parameters if p.required}
        provided_names = set(args.keys())

        missing = required_names - provided_names
        if missing:
            return False, f"Missing required parameters: {missing}"

        # No unknown parameters
        allowed_names = {p.name for p in self.parameters}
        extra = provided_names - allowed_names
        if extra:
            return False, f"Unknown parameters: {extra}"

        return True, None


# AgentDojo v0.1.35 banking suite tools
# Source: THREAT.md scenario definition, AgentDojo environment schema
BANKING_TOOLS = (
    ToolSchema(
        name="send_money",
        parameters=(
            ToolParameter(name="to", required=True),
            ToolParameter(name="amount", required=True),
        ),
    ),
    ToolSchema(
        name="list_transactions",
        parameters=(
            ToolParameter(name="limit", required=False),
        ),
    ),
    ToolSchema(
        name="get_balance",
        parameters=(),
    ),
)

# Registry: tool name -> schema
_TOOL_SCHEMAS = {tool.name: tool for tool in BANKING_TOOLS}


def get_tool_schema(tool_name: str) -> ToolSchema | None:
    """Look up schema for a tool by name.

    Returns None if the tool is not in the registry (untrusted proposal).
    """
    return _TOOL_SCHEMAS.get(tool_name)


def validate_tool_call(tool: str, args: dict) -> tuple[bool, str | None]:
    """Validate a proposed tool call against the known schema.

    Returns (is_valid, error_message).
    """
    schema = get_tool_schema(tool)
    if not schema:
        return False, f"Unknown tool: {tool}"
    return schema.validate_args(args)


def scope_for_tool(tool: str, args: dict, schema: ToolSchema | None = None) -> tuple[tuple[str, object], ...]:
    """Generate scope constraints for a tool call.

    For P0 (tight scoping), this includes ALL parameters (required and optional)
    that are present in args. This ensures that an injected call with different
    parameter values cannot match the minted capability.

    Args:
        tool: Tool name
        args: Proposed arguments (assumed to be validated)
        schema: Optional pre-fetched schema; if None, looked up by tool name

    Returns:
        Tuple of (param_name, value) pairs for capability scope
    """
    if schema is None:
        schema = get_tool_schema(tool)
    if not schema:
        return ()

    # Include all parameters that are present in args, in scope
    # This ensures tight coupling: capability matches *exactly* the authorized call
    scope_pairs = []
    for param in schema.parameters:
        if param.name in args:
            scope_pairs.append((param.name, args[param.name]))

    return tuple(scope_pairs)
