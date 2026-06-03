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
