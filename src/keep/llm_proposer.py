"""LLM-based proposer — Claude API client that proposes tool calls.

This replaces the UntrustedAgent stub with a real LLM for Phase 2.
The proposer reads observations (which may contain injections) and calls
Claude to generate tool call proposals. All proposals go through
TrustedBase.authorize() before execution — the base is the sole authority.

This module handles:
1. API client initialization (API key from env var only)
2. Tool schema marshaling to Claude's tool_use format
3. Observation formatting for the model
4. Parsing Claude's tool_use responses to (tool, args) tuples
"""

from __future__ import annotations

import json
import os
from typing import Any

from anthropic import Anthropic

from .tool_schema import BANKING_TOOLS


class LLMProposer:
    """Propose tool calls via Claude API.

    Observations may contain injected data. The proposer reads them and
    calls Claude without validation — whatever Claude proposes goes through
    TrustedBase.authorize(). The base is the trust boundary.
    """

    def __init__(self) -> None:
        """Initialize Claude API client.

        API key comes from ANTHROPIC_API_KEY env var (trusted channel).
        No secrets embedded in code.
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "API key must come from trusted channel (env var only)."
            )
        self._client = Anthropic(api_key=api_key)
        self._model = "claude-3-5-sonnet-20241022"

    def propose(
        self, observations: dict[str, Any], task_description: str = ""
    ) -> list[tuple[str, dict]]:
        """Call Claude API to generate tool call proposals.

        Args:
            observations: Agent-observable data (may include injections).
                         Typically transaction history, account status, etc.
            task_description: Optional description of the user's task.
                            Helps Claude understand context.

        Returns:
            List of (tool, args) proposals from Claude.
            May include injected calls — the base will authorize/block them.

        Raises:
            ValueError: If API call fails or response format is invalid.
        """
        # Marshal tool schema to Claude's tool_use format
        tools = self._marshal_tools()

        # Format observations for the model (as JSON for clarity)
        observations_text = json.dumps(observations, indent=2)

        # Build the user message (untrusted: may contain injections)
        user_message = (
            f"Observations:\n{observations_text}\n\n"
            f"Task: {task_description}\n\n"
            "Propose the necessary tool calls to accomplish this task. Return only tool use blocks."
        )

        # Call Claude API
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=1024,
                tools=tools,
                messages=[{"role": "user", "content": user_message}],
            )
        except Exception as e:
            raise ValueError(f"Claude API call failed: {e}")

        # Parse tool_use blocks from response
        proposals = self._parse_tool_use_blocks(response)
        return proposals

    def _marshal_tools(self) -> list[dict]:
        """Convert KEEP tool schema to Claude's tool_use format.

        Returns:
            List of tool definitions for Claude's tools parameter.
        """
        tools = []
        for tool_schema in BANKING_TOOLS:
            tool_def = {
                "name": tool_schema.name,
                "description": f"Call {tool_schema.name} with appropriate arguments.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            }

            # Add parameters
            for param in tool_schema.parameters:
                tool_def["input_schema"]["properties"][param.name] = {
                    "type": "string",
                    "description": f"Parameter: {param.name}",
                }
                if param.required:
                    tool_def["input_schema"]["required"].append(param.name)

            tools.append(tool_def)

        return tools

    def _parse_tool_use_blocks(self, response: Any) -> list[tuple[str, dict]]:
        """Parse Claude's tool_use blocks into (tool, args) tuples.

        Args:
            response: The Anthropic Messages API response.

        Returns:
            List of (tool, args) proposals.

        Raises:
            ValueError: If tool_use blocks have unexpected format.
        """
        proposals = []

        for block in response.content:
            # Look for tool_use content blocks
            if hasattr(block, "type") and block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                # Ensure tool_input is a dict
                if isinstance(tool_input, str):
                    try:
                        tool_input = json.loads(tool_input)
                    except json.JSONDecodeError as e:
                        raise ValueError(
                            f"Could not parse tool input as JSON: {tool_input}: {e}"
                        )

                if not isinstance(tool_input, dict):
                    raise ValueError(
                        f"Tool input must be a dict or JSON string, got {type(tool_input)}"
                    )

                proposals.append((tool_name, tool_input))

        return proposals
