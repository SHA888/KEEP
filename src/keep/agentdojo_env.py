"""AgentDojo banking-suite environment integration.

This module sets up a real AgentDojo banking environment and provides tool
execution functions. All tool calls are routed through TrustedBase.authorize()
before execution (see runner.py).

The environment is initialized with a scenario and user profile from AgentDojo's
v0.1.35 banking suite. Tools are executed by calling the AgentDojo environment's
methods, not by mocking them.
"""
from __future__ import annotations

from typing import Callable


class AgentDojoEnvironment:
    """Wrapper around AgentDojo banking environment for P0 testing.

    This loads the AgentDojo v0.1.35 banking suite scenario specified in THREAT.md.
    Tool execution is deferred to caller (typically through a TrustedBase.execute effect).
    """

    def __init__(self, scenario_id: str = "injection_incoming_transaction"):
        """Initialize AgentDojo banking environment.

        Args:
            scenario_id: AgentDojo scenario ID (default from THREAT.md)
        """
        try:
            import agentdojo
        except ImportError:
            raise ImportError(
                "agentdojo package not found. Install with: pip install agentdojo==0.1.35"
            )

        # Load the banking suite scenario
        # AgentDojo v0.1.35 structure: Benchmark > Suite > Scenario
        try:
            benchmark = agentdojo.Benchmark("banking", "v0.1.35")
            self.scenario = benchmark.scenarios[scenario_id]
        except (KeyError, AttributeError) as e:
            raise ValueError(
                f"Could not load scenario {scenario_id} from AgentDojo banking suite. "
                f"Ensure agentdojo==0.1.35 is installed and scenario exists. Error: {e}"
            )

        # Store the scenario for tool execution
        self._scenario = self.scenario

    def get_tool_executor(self) -> Callable[[str, dict], object]:
        """Return an effect function for TrustedBase.execute().

        The returned function executes AgentDojo tools in the loaded scenario.
        All calls must be authorized by TrustedBase before this is invoked.

        Returns:
            Callable that executes (tool, args) and returns result
        """
        def execute_tool(tool: str, args: dict) -> object:
            """Execute a tool in the AgentDojo environment.

            This is called by TrustedBase.execute() after authorization.
            The tool call has already been validated against a minted capability.

            Args:
                tool: Tool name (e.g., "send_money")
                args: Tool arguments as dict (e.g., {"to": "alice@b.com", "amount": 100})

            Returns:
                Tool execution result (depends on tool)

            Raises:
                AttributeError: If tool not found in scenario
                ValueError: If tool execution fails
            """
            # Get the tool from the scenario environment
            # AgentDojo scenarios expose tools as methods on the environment
            if not hasattr(self._scenario, tool):
                raise AttributeError(
                    f"Tool '{tool}' not found in scenario. "
                    f"Available tools: {self._get_available_tools()}"
                )

            tool_func = getattr(self._scenario, tool)

            # Execute the tool with the provided arguments
            try:
                return tool_func(**args)
            except TypeError as e:
                raise ValueError(
                    f"Tool '{tool}' call failed with args {args}: {e}"
                )

        return execute_tool

    def _get_available_tools(self) -> list[str]:
        """List all tools available in the scenario (for error messages)."""
        # AgentDojo scenarios typically expose tools as attributes
        return [
            attr
            for attr in dir(self._scenario)
            if not attr.startswith("_") and callable(getattr(self._scenario, attr))
        ]

    def get_scenario_context(self) -> dict:
        """Get scenario context (user profile, initial state, etc.).

        Returns:
            Dict with scenario metadata
        """
        return {
            "scenario_id": self._scenario.name if hasattr(self._scenario, "name") else "unknown",
            "available_tools": self._get_available_tools(),
        }
