"""Test adapter: AgentDojo banking scenario -> KEEP deriver input."""

import pytest
from keep.adapter import adapt_banking_scenario, trusted_instruction_to_deriver_input
from keep.deriver import derive


def test_adapt_banking_scenario_rent_payment():
    """Adapter converts banking-scenario rent-payment task to trusted instruction."""
    user_task = "Pay my rent of $1500 to landlord@example.com"
    instruction = adapt_banking_scenario(user_task)

    assert instruction.action == "pay_rent"
    assert instruction.to == "landlord@example.com"
    assert instruction.amount == 1500.0


def test_adapt_banking_scenario_extracts_amount():
    """Adapter correctly extracts various amount formats."""
    test_cases = [
        ("Pay $1500 for rent", 1500.0),
        ("Pay 1500 for rent", 1500.0),
        ("Pay $1,500.50 for rent", 1500.50),
        ("Pay $100.5 for rent", 100.5),  # Single decimal digit
        ("Pay $99.9 for rent", 99.9),    # Single decimal digit
        ("Pay $50.123 for rent", 50.123),  # Multiple decimal digits
    ]
    for task, expected_amount in test_cases:
        instruction = adapt_banking_scenario(task)
        assert instruction.amount == expected_amount


def test_adapt_banking_scenario_extracts_recipient():
    """Adapter extracts recipient email from task."""
    task = "Pay my rent of $1500 to landlord@test.com"
    instruction = adapt_banking_scenario(task)
    assert instruction.to == "landlord@test.com"


def test_adapter_to_deriver_format():
    """Adapted instruction converts to deriver input format."""
    user_task = "Pay my rent of $1500 to landlord@example.com"
    instruction = adapt_banking_scenario(user_task)
    deriver_input = trusted_instruction_to_deriver_input(instruction)

    assert deriver_input == {
        "action": "pay_rent",
        "to": "landlord@example.com",
        "amount": 1500.0,
    }


def test_adapter_output_works_with_deriver():
    """Adapter output can be minted into capabilities by deriver."""
    user_task = "Pay my rent of $1500 to landlord@example.com"
    instruction = adapt_banking_scenario(user_task)
    deriver_input = trusted_instruction_to_deriver_input(instruction)

    # Deriver should mint exactly one capability
    caps = derive(deriver_input)
    assert len(caps) == 1
    assert caps[0].tool == "send_money"
    assert ("to", "landlord@example.com") in caps[0].scope
    assert ("amount", 1500.0) in caps[0].scope


def test_adapter_rejects_unrecognized_task():
    """Adapter rejects tasks that don't match known patterns."""
    with pytest.raises(ValueError, match="Unrecognized task"):
        adapt_banking_scenario("Do some random banking task")


def test_adapter_rejects_task_without_amount():
    """Adapter rejects rent task without amount."""
    with pytest.raises(ValueError, match="Cannot extract amount"):
        adapt_banking_scenario("Pay my rent to landlord@example.com")


# Tests for task 1.5: tool schema and capability scope


def test_validate_tool_call_send_money_valid():
    """Tool call validation accepts valid send_money calls."""
    from keep.adapter import validate_agentdojo_tool_call

    is_valid, error = validate_agentdojo_tool_call(
        "send_money",
        {"to": "alice@example.com", "amount": 100.0}
    )
    assert is_valid
    assert error is None


def test_validate_tool_call_send_money_missing_required():
    """Tool call validation rejects send_money without required 'to'."""
    from keep.adapter import validate_agentdojo_tool_call

    is_valid, error = validate_agentdojo_tool_call(
        "send_money",
        {"amount": 100.0}  # missing 'to'
    )
    assert not is_valid
    assert "Missing required parameters" in error


def test_validate_tool_call_unknown_parameter():
    """Tool call validation rejects calls with unknown parameters."""
    from keep.adapter import validate_agentdojo_tool_call

    is_valid, error = validate_agentdojo_tool_call(
        "send_money",
        {"to": "alice@example.com", "amount": 100.0, "memo": "rent"}
    )
    assert not is_valid
    assert "Unknown parameters" in error


def test_validate_tool_call_unknown_tool():
    """Tool call validation rejects unknown tool names."""
    from keep.adapter import validate_agentdojo_tool_call

    is_valid, error = validate_agentdojo_tool_call(
        "unknown_tool",
        {}
    )
    assert not is_valid
    assert "Unknown tool" in error


def test_validate_tool_call_list_transactions_valid():
    """Tool call validation accepts list_transactions with optional limit."""
    from keep.adapter import validate_agentdojo_tool_call

    # With limit
    is_valid, error = validate_agentdojo_tool_call(
        "list_transactions",
        {"limit": 10}
    )
    assert is_valid

    # Without limit (optional)
    is_valid, error = validate_agentdojo_tool_call(
        "list_transactions",
        {}
    )
    assert is_valid


def test_validate_tool_call_get_balance_valid():
    """Tool call validation accepts get_balance with no parameters."""
    from keep.adapter import validate_agentdojo_tool_call

    is_valid, error = validate_agentdojo_tool_call(
        "get_balance",
        {}
    )
    assert is_valid


def test_capability_scope_for_tool_send_money():
    """Scope generation includes all required send_money parameters."""
    from keep.adapter import capability_scope_for_tool_call

    scope = capability_scope_for_tool_call(
        "send_money",
        {"to": "landlord@example.com", "amount": 1500.0}
    )

    # Scope should constrain both 'to' and 'amount'
    assert ("to", "landlord@example.com") in scope
    assert ("amount", 1500.0) in scope
    assert len(scope) == 2


def test_capability_scope_for_tool_list_transactions():
    """Scope generation for list_transactions constrains optional parameters."""
    from keep.adapter import capability_scope_for_tool_call

    # With limit
    scope = capability_scope_for_tool_call(
        "list_transactions",
        {"limit": 10}
    )
    assert ("limit", 10) in scope

    # Without limit
    scope = capability_scope_for_tool_call(
        "list_transactions",
        {}
    )
    assert len(scope) == 0  # No required parameters


def test_capability_scope_for_tool_get_balance():
    """Scope generation for get_balance is empty (no parameters)."""
    from keep.adapter import capability_scope_for_tool_call

    scope = capability_scope_for_tool_call(
        "get_balance",
        {}
    )
    assert len(scope) == 0


def test_injection_blocked_by_scope_to_parameter():
    """Injection scenario: injected send_money with wrong 'to' is blocked."""
    from keep.adapter import (
        adapt_banking_scenario,
        trusted_instruction_to_deriver_input,
    )

    # User authorizes: pay rent to landlord
    user_task = "Pay my rent of $1500 to landlord@example.com"
    instruction = adapt_banking_scenario(user_task)
    deriver_input = trusted_instruction_to_deriver_input(instruction)

    # Deriver mints capability from trusted input
    caps = derive(deriver_input)
    assert len(caps) == 1
    minted_cap = caps[0]

    # Legitimate call: landlord@example.com, amount 1500
    legitimate_args = {"to": "landlord@example.com", "amount": 1500.0}
    assert minted_cap.authorizes("send_money", legitimate_args)

    # Injection attempt: attacker@evil.com, amount 10000 (from THREAT.md scenario)
    injected_args = {"to": "attacker@evil.com", "amount": 10000.0}
    assert not minted_cap.authorizes("send_money", injected_args)


def test_list_available_tools():
    """Adapter enumerates all available banking tools."""
    from keep.adapter import list_available_tools

    tools = list_available_tools()
    assert "send_money" in tools
    assert "list_transactions" in tools
    assert "get_balance" in tools
    assert len(tools) == 3
